import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import BigInteger, create_engine, event, select
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, configure_mappers

import app.models
from app.api.dependencies import (
    _authenticated_user_id,
    get_current_customer,
    get_current_delivery_partner,
)
from app.api.categories import read_restaurant_categories
from app.api.cuisines import read_restaurant_cuisines
from app.api.restaurants import (
    read_restaurant,
    read_restaurant_menu,
    read_restaurants,
)
from app.core.security import create_access_token, verify_password
from app.db.base_class import Base
from app.models.addon import Addon, AddonGroup, MenuItemAddonGroup
from app.models.category import (
    Cuisine,
    FoodCategory,
    RestaurantCategory,
    RestaurantCuisine,
)
from app.models.coupon import Coupon, OrderCoupon
from app.models.delivery import DeliveryAssignment
from app.models.history import OrderStatusHistory
from app.models.menu import MenuItem
from app.models.order import OrderItem
from app.models.payment import Payment, PaymentMethod
from app.models.restaurant import Restaurant
from app.models.review import FoodItemReview, RestaurantReview
from app.models.user import (
    Customer,
    DeliveryPartner,
    RestaurantOwner,
    Role,
    User,
    UserRole,
)
from app.schemas.cart import CartAddonRequest, CartItemCreate
from app.schemas.coupon import CouponApplyRequest
from app.schemas.delivery import DeliveryTrackingCreate
from app.schemas.review import ReviewUpdate
from app.services.auth import get_active_user_by_email, register_customer
from app.services.cart import MenuItemUnavailable, add_cart_item
from app.services.category import list_active_categories, list_restaurant_categories
from app.services.coupon import (
    CouponNotEligible,
    OrderCouponAlreadyApplied,
    apply_coupon_to_order,
    remove_coupon_from_order,
)
from app.services.cuisine import list_active_cuisines, list_restaurant_cuisines
from app.services.delivery import (
    AssignmentNotFound,
    OrderNotFound as TrackingOrderNotFound,
    add_tracking_point,
    get_partner_assignment,
    list_customer_order_tracking,
    list_partner_assignments,
)
from app.services.order import (
    ActiveCartNotFound,
    OrderNotFound,
    cancel_order,
    create_order,
    get_order,
)
from app.services.payment import (
    OrderNotFound as PaymentOrderNotFound,
    PaymentMethodNotFound,
    PaymentNotFound,
    create_payment_record,
    get_customer_payment,
)
from app.api.coupons import apply_order_coupon, delete_order_coupon
from app.services.restaurant import (
    get_active_restaurant,
    list_active_restaurants,
    list_restaurant_menu_items,
)
from app.services.review import (
    DuplicateReview,
    PurchaseNotFound,
    ReviewNotFound,
    create_food_item_review,
    create_restaurant_review,
    delete_food_item_review,
    delete_restaurant_review,
    list_food_item_reviews,
    list_restaurant_reviews,
    update_restaurant_review,
)


@compiles(BigInteger, "sqlite")
def _compile_bigint_as_integer(type_, compiler, **kwargs):
    return "INTEGER"


class BackendIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        configure_mappers()
        self.engine = create_engine("sqlite:///:memory:")
        event.listen(self.engine, "connect", self._enable_sqlite_foreign_keys)
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self._user_counter = 0

        self.customer_user = self._user("customer")
        self.customer = Customer(user_id=self.customer_user.user_id, status=1)
        self.second_customer_user = self._user("second-customer")
        self.second_customer = Customer(
            user_id=self.second_customer_user.user_id,
            status=1,
        )
        self.owner_user = self._user("owner")
        self.owner = RestaurantOwner(user_id=self.owner_user.user_id, status=1)
        self.partner_user = self._user("partner")
        self.partner = DeliveryPartner(
            user_id=self.partner_user.user_id,
            verification_status="PENDING",
            availability_status="AVAILABLE",
            status=1,
        )
        self.second_partner_user = self._user("second-partner")
        self.second_partner = DeliveryPartner(
            user_id=self.second_partner_user.user_id,
            verification_status="PENDING",
            availability_status="AVAILABLE",
            status=1,
        )
        self.db.add_all(
            [
                self.customer,
                self.second_customer,
                self.owner,
                self.partner,
                self.second_partner,
            ]
        )
        self.db.flush()

        self.category = FoodCategory(category_name="Integration Food", status=1)
        self.cuisine = Cuisine(cuisine_name="Integration Cuisine", status=1)
        self.db.add_all([self.category, self.cuisine])
        self.db.flush()
        self.restaurant = Restaurant(
            owner_id=self.owner.owner_id,
            restaurant_name="Integration Restaurant",
            restaurant_status="APPROVED",
            status=1,
        )
        self.db.add(self.restaurant)
        self.db.flush()
        self.db.add_all(
            [
                RestaurantCategory(
                    restaurant_id=self.restaurant.restaurant_id,
                    category_id=self.category.category_id,
                    status=1,
                ),
                RestaurantCuisine(
                    restaurant_id=self.restaurant.restaurant_id,
                    cuisine_id=self.cuisine.cuisine_id,
                    status=1,
                ),
            ]
        )
        self.item = MenuItem(
            restaurant_id=self.restaurant.restaurant_id,
            category_id=self.category.category_id,
            item_name="Integration Dish",
            base_price=Decimal("10.00"),
            status=1,
            is_available=True,
        )
        self.group = AddonGroup(
            restaurant_id=self.restaurant.restaurant_id,
            group_name="Extras",
            is_required=False,
            min_selection=0,
            max_selection=2,
            status=1,
        )
        self.db.add_all([self.item, self.group])
        self.db.flush()
        self.addon = Addon(
            addon_group_id=self.group.addon_group_id,
            addon_name="Extra sauce",
            additional_price=Decimal("2.00"),
            is_available=True,
            status=1,
        )
        self.db.add_all(
            [
                self.addon,
                MenuItemAddonGroup(
                    item_id=self.item.item_id,
                    addon_group_id=self.group.addon_group_id,
                    status=1,
                ),
            ]
        )
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    @staticmethod
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def _user(self, suffix: str) -> User:
        self._user_counter += 1
        user = User(
            full_name=suffix.title(),
            email=f"{suffix}@example.test",
            phone=f"555{self._user_counter:08d}",
            password_hash="unused-test-hash",
            status=1,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def _create_order(self, quantity: int = 1, with_addon: bool = False):
        selected_addons = (
            [CartAddonRequest(addon_id=self.addon.addon_id, quantity=2)]
            if with_addon
            else []
        )
        add_cart_item(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            request=CartItemCreate(
                menu_item_id=self.item.item_id,
                quantity=quantity,
                selected_addons=selected_addons,
            ),
        )
        return create_order(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
        )

    def test_registration_password_hash_jwt_and_customer_auth(self) -> None:
        role = Role(role_name="Customer", status=1)
        self.db.add(role)
        self.db.commit()

        user, customer = register_customer(
            self.db,
            full_name="New Customer",
            email="new@example.test",
            phone="555-new",
            password="long-test-password",
        )
        self.assertEqual(customer.user_id, user.user_id)
        self.assertTrue(
            verify_password("long-test-password", user.password_hash)
        )
        self.assertFalse(verify_password("wrong-password", user.password_hash))
        self.assertEqual(
            get_active_user_by_email(self.db, user.email).user_id,
            user.user_id,
        )
        self.assertEqual(
            self.db.scalar(
                select(UserRole.user_id).where(UserRole.user_id == user.user_id)
            ),
            user.user_id,
        )

        with patch("app.core.security.JWT_SECRET_KEY", "s" * 40), patch(
            "app.api.dependencies.JWT_SECRET_KEY",
            "s" * 40,
        ):
            token = create_access_token(str(user.user_id))
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=token,
            )
            self.assertEqual(_authenticated_user_id(credentials), user.user_id)
            self.assertEqual(
                get_current_customer(credentials, self.db).customer_id,
                customer.customer_id,
            )
            with self.assertRaises(HTTPException):
                _authenticated_user_id(
                    HTTPAuthorizationCredentials(
                        scheme="Bearer",
                        credentials="not-a-valid-token",
                    )
                )

    def test_public_browsing_requires_approved_active_restaurant(self) -> None:
        non_public_restaurants = []
        for name, restaurant_status, status in (
            ("Pending Restaurant", "PENDING", 1),
            ("Inactive Restaurant", "APPROVED", 0),
        ):
            restaurant = Restaurant(
                owner_id=self.owner.owner_id,
                restaurant_name=name,
                restaurant_status=restaurant_status,
                status=status,
            )
            self.db.add(restaurant)
            self.db.flush()
            self.db.add_all(
                [
                    RestaurantCategory(
                        restaurant_id=restaurant.restaurant_id,
                        category_id=self.category.category_id,
                        status=1,
                    ),
                    RestaurantCuisine(
                        restaurant_id=restaurant.restaurant_id,
                        cuisine_id=self.cuisine.cuisine_id,
                        status=1,
                    ),
                    MenuItem(
                        restaurant_id=restaurant.restaurant_id,
                        category_id=self.category.category_id,
                        item_name=f"{name} Dish",
                        base_price=Decimal("5.00"),
                        status=1,
                        is_available=True,
                    ),
                ]
            )
            non_public_restaurants.append(restaurant)
        self.db.commit()

        self.assertEqual(
            [row.restaurant_id for row in read_restaurants(self.db)],
            [self.restaurant.restaurant_id],
        )
        self.assertEqual(
            read_restaurant(self.restaurant.restaurant_id, self.db).restaurant_id,
            self.restaurant.restaurant_id,
        )
        self.assertEqual(
            [row.item_name for row in read_restaurant_menu(
                self.restaurant.restaurant_id, self.db
            )],
            ["Integration Dish"],
        )
        self.assertEqual(
            [row.category_id for row in read_restaurant_categories(
                self.restaurant.restaurant_id, self.db
            )],
            [self.category.category_id],
        )
        self.assertEqual(
            [row.cuisine_id for row in read_restaurant_cuisines(
                self.restaurant.restaurant_id, self.db
            )],
            [self.cuisine.cuisine_id],
        )

        for restaurant in non_public_restaurants:
            restaurant_id = restaurant.restaurant_id
            self.assertIsNone(get_active_restaurant(self.db, restaurant_id))
            self.assertEqual(list_restaurant_menu_items(self.db, restaurant_id), [])
            self.assertEqual(list_restaurant_categories(self.db, restaurant_id), [])
            self.assertEqual(list_restaurant_cuisines(self.db, restaurant_id), [])
            for endpoint in (
                lambda rid=restaurant_id: read_restaurant(rid, self.db),
                lambda rid=restaurant_id: read_restaurant_menu(rid, self.db),
                lambda rid=restaurant_id: read_restaurant_categories(rid, self.db),
                lambda rid=restaurant_id: read_restaurant_cuisines(rid, self.db),
            ):
                with self.assertRaises(HTTPException) as raised:
                    endpoint()
                self.assertEqual(raised.exception.status_code, 404)

    def test_browse_cart_order_coupon_payment_and_cancellation(self) -> None:
        self.assertIsNotNone(
            get_active_restaurant(self.db, self.restaurant.restaurant_id)
        )
        self.assertEqual(
            [row.category_id for row in list_active_categories(self.db)],
            [self.category.category_id],
        )
        self.assertEqual(
            [row.category_id for row in list_restaurant_categories(
                self.db, self.restaurant.restaurant_id
            )],
            [self.category.category_id],
        )
        self.assertEqual(
            [row.cuisine_id for row in list_active_cuisines(self.db)],
            [self.cuisine.cuisine_id],
        )
        self.assertEqual(
            [row.cuisine_id for row in list_restaurant_cuisines(
                self.db, self.restaurant.restaurant_id
            )],
            [self.cuisine.cuisine_id],
        )
        self.assertEqual(
            [row.item_id for row in list_restaurant_menu_items(
                self.db, self.restaurant.restaurant_id
            )],
            [self.item.item_id],
        )
        self.assertEqual(
            [row.restaurant_id for row in list_active_restaurants(self.db)],
            [self.restaurant.restaurant_id],
        )
        with self.assertRaises(ActiveCartNotFound):
            create_order(
                self.db,
                customer_id=self.customer.customer_id,
                user_id=self.customer_user.user_id,
            )
        with self.assertRaises(MenuItemUnavailable):
            add_cart_item(
                self.db,
                customer_id=self.customer.customer_id,
                user_id=self.customer_user.user_id,
                request=CartItemCreate(
                    menu_item_id=self.item.item_id + 999,
                    quantity=1,
                ),
            )

        cart = add_cart_item(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            request=CartItemCreate(
                menu_item_id=self.item.item_id,
                quantity=2,
                selected_addons=[
                    CartAddonRequest(addon_id=self.addon.addon_id, quantity=2)
                ],
            ),
        )
        self.assertEqual(cart.total_amount, Decimal("28.00"))
        order = create_order(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
        )
        self.assertEqual(order.subtotal, Decimal("28.00"))
        self.assertEqual(order.items[0].total_price, Decimal("28.00"))
        self.assertEqual(order.items[0].addons[0].total_price, Decimal("8.00"))

        coupon = Coupon(
            coupon_code="SAVE20",
            discount_type="PERCENTAGE",
            discount_value=Decimal("20.00"),
            maximum_discount=Decimal("4.00"),
            minimum_order_amount=Decimal("20.00"),
            usage_limit=1,
            per_user_limit=1,
            is_active=True,
            status=1,
        )
        method = PaymentMethod(method_name="Cash", status=1)
        expired_coupon = Coupon(
            coupon_code="EXPIRED",
            discount_type="FIXED",
            discount_value=Decimal("1.00"),
            valid_until=datetime.now(timezone.utc).replace(tzinfo=None)
            - timedelta(days=1),
            is_active=True,
            status=1,
        )
        self.db.add_all([coupon, expired_coupon, method])
        self.db.commit()
        with self.assertRaises(CouponNotEligible):
            apply_coupon_to_order(
                self.db,
                customer_id=self.customer.customer_id,
                user_id=self.customer_user.user_id,
                order_id=order.order_id,
                coupon_id=expired_coupon.coupon_id,
            )
        applied = apply_coupon_to_order(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            order_id=order.order_id,
            coupon_id=coupon.coupon_id,
        )
        self.assertEqual(applied.discount_amount, Decimal("4.00"))
        self.assertEqual(applied.total_amount, Decimal("24.00"))
        with self.assertRaises(OrderCouponAlreadyApplied):
            apply_coupon_to_order(
                self.db,
                customer_id=self.customer.customer_id,
                user_id=self.customer_user.user_id,
                order_id=order.order_id,
                coupon_id=coupon.coupon_id,
            )

        remove_coupon_from_order(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            order_id=order.order_id,
            order_coupon_id=applied.order_coupon_id,
        )
        restored_order = get_order(
            self.db,
            customer_id=self.customer.customer_id,
            order_id=order.order_id,
        )
        self.assertEqual(restored_order.item_discount, Decimal("0.00"))
        self.assertEqual(restored_order.total_amount, Decimal("28.00"))
        self.assertEqual(restored_order.payment_status, "PENDING")

        payment = create_payment_record(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            order_id=order.order_id,
            payment_method_id=method.payment_method_id,
        )
        self.assertEqual(payment.amount, Decimal("28.00"))
        self.assertEqual(payment.payment_status, "PENDING")
        with self.assertRaises(PaymentOrderNotFound):
            create_payment_record(
                self.db,
                customer_id=self.second_customer.customer_id,
                user_id=self.second_customer_user.user_id,
                order_id=order.order_id,
                payment_method_id=method.payment_method_id,
            )
        with self.assertRaises(PaymentMethodNotFound):
            create_payment_record(
                self.db,
                customer_id=self.customer.customer_id,
                user_id=self.customer_user.user_id,
                order_id=order.order_id,
                payment_method_id=method.payment_method_id + 999,
            )
        with self.assertRaises(PaymentNotFound):
            get_customer_payment(
                self.db,
                customer_id=self.second_customer.customer_id,
                payment_id=payment.payment_id,
            )

        cancelled_order = cancel_order(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            order_id=order.order_id,
            cancellation_reason="Changed plans",
        )
        self.assertEqual(cancelled_order.order_status, "CANCELLED")
        history = self.db.scalar(
            select(OrderStatusHistory).where(
                OrderStatusHistory.order_id == order.order_id
            )
        )
        self.assertEqual(history.old_status, "PLACED")
        self.assertEqual(history.new_status, "CANCELLED")
        with self.assertRaises(OrderNotFound):
            get_order(
                self.db,
                customer_id=self.second_customer.customer_id,
                order_id=order.order_id,
            )

    def test_coupon_apply_and_remove_are_allowed_without_payment(self) -> None:
        order = self._create_order()
        coupon = Coupon(
            coupon_code="BEFOREPAY",
            discount_type="FIXED",
            discount_value=Decimal("2.00"),
            is_active=True,
            status=1,
        )
        self.db.add(coupon)
        self.db.commit()

        applied = apply_coupon_to_order(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            order_id=order.order_id,
            coupon_id=coupon.coupon_id,
        )
        self.assertEqual(applied.total_amount, Decimal("8.00"))
        remove_coupon_from_order(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            order_id=order.order_id,
            order_coupon_id=applied.order_coupon_id,
        )
        restored = get_order(
            self.db,
            customer_id=self.customer.customer_id,
            order_id=order.order_id,
        )
        self.assertEqual(restored.total_amount, Decimal("10.00"))
        self.assertEqual(restored.item_discount, Decimal("0.00"))
        self.assertIsNone(
            self.db.get(OrderCoupon, applied.order_coupon_id)
        )

    def test_pending_payment_rejects_coupon_application_without_changes(
        self,
    ) -> None:
        order = self._create_order()
        coupon = Coupon(
            coupon_code="NOAPPLY",
            discount_type="FIXED",
            discount_value=Decimal("2.00"),
            is_active=True,
            status=1,
        )
        method = PaymentMethod(method_name="Pending Apply", status=1)
        self.db.add_all([coupon, method])
        self.db.commit()
        payment = create_payment_record(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            order_id=order.order_id,
            payment_method_id=method.payment_method_id,
        )
        self.assertEqual(payment.payment_status, "PENDING")
        before = get_order(
            self.db,
            customer_id=self.customer.customer_id,
            order_id=order.order_id,
        )

        with self.assertRaises(HTTPException) as raised:
            apply_order_coupon(
                CouponApplyRequest(coupon_id=coupon.coupon_id),
                order_id=order.order_id,
                customer=self.customer,
                db=self.db,
            )
        self.assertEqual(raised.exception.status_code, 409)

        after = get_order(
            self.db,
            customer_id=self.customer.customer_id,
            order_id=order.order_id,
        )
        self.assertEqual(after.total_amount, before.total_amount)
        self.assertEqual(after.item_discount, before.item_discount)
        self.assertIsNone(
            self.db.scalar(
                select(OrderCoupon.id).where(
                    OrderCoupon.order_id == order.order_id
                )
            )
        )
        self.assertEqual(
            self.db.get(Payment, payment.payment_id).payment_status,
            "PENDING",
        )

    def test_pending_payment_rejects_coupon_removal_without_changes(self) -> None:
        order = self._create_order()
        coupon = Coupon(
            coupon_code="NOREMOVE",
            discount_type="FIXED",
            discount_value=Decimal("2.00"),
            is_active=True,
            status=1,
        )
        method = PaymentMethod(method_name="Pending Remove", status=1)
        self.db.add_all([coupon, method])
        self.db.commit()
        applied = apply_coupon_to_order(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            order_id=order.order_id,
            coupon_id=coupon.coupon_id,
        )
        payment = create_payment_record(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            order_id=order.order_id,
            payment_method_id=method.payment_method_id,
        )
        self.assertEqual(payment.payment_status, "PENDING")
        before = get_order(
            self.db,
            customer_id=self.customer.customer_id,
            order_id=order.order_id,
        )

        with self.assertRaises(HTTPException) as raised:
            delete_order_coupon(
                order_id=order.order_id,
                order_coupon_id=applied.order_coupon_id,
                customer=self.customer,
                db=self.db,
            )
        self.assertEqual(raised.exception.status_code, 409)

        after = get_order(
            self.db,
            customer_id=self.customer.customer_id,
            order_id=order.order_id,
        )
        self.assertEqual(after.total_amount, before.total_amount)
        self.assertEqual(after.item_discount, before.item_discount)
        self.assertIsNotNone(self.db.get(OrderCoupon, applied.order_coupon_id))
        self.assertEqual(
            self.db.get(Payment, payment.payment_id).payment_status,
            "PENDING",
        )

    def test_coupon_operations_cannot_access_another_customers_order(self) -> None:
        order = self._create_order()
        coupon = Coupon(
            coupon_code="OWNERONLY",
            discount_type="FIXED",
            discount_value=Decimal("2.00"),
            is_active=True,
            status=1,
        )
        self.db.add(coupon)
        self.db.commit()

        with self.assertRaises(HTTPException) as apply_error:
            apply_order_coupon(
                CouponApplyRequest(coupon_id=coupon.coupon_id),
                order_id=order.order_id,
                customer=self.second_customer,
                db=self.db,
            )
        self.assertEqual(apply_error.exception.status_code, 404)

        applied = apply_coupon_to_order(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            order_id=order.order_id,
            coupon_id=coupon.coupon_id,
        )
        before = get_order(
            self.db,
            customer_id=self.customer.customer_id,
            order_id=order.order_id,
        )
        with self.assertRaises(HTTPException) as remove_error:
            delete_order_coupon(
                order_id=order.order_id,
                order_coupon_id=applied.order_coupon_id,
                customer=self.second_customer,
                db=self.db,
            )
        self.assertEqual(remove_error.exception.status_code, 404)
        after = get_order(
            self.db,
            customer_id=self.customer.customer_id,
            order_id=order.order_id,
        )
        self.assertEqual(after.total_amount, before.total_amount)
        self.assertIsNotNone(self.db.get(OrderCoupon, applied.order_coupon_id))

    def test_delivery_tracking_and_review_ownership(self) -> None:
        order = self._create_order()
        assignment = DeliveryAssignment(
            order_id=order.order_id,
            partner_id=self.partner.partner_id,
            assignment_status="ASSIGNED",
            status=1,
        )
        self.db.add(assignment)
        self.db.commit()

        with patch("app.core.security.JWT_SECRET_KEY", "s" * 40), patch(
            "app.api.dependencies.JWT_SECRET_KEY",
            "s" * 40,
        ):
            partner_token = create_access_token(str(self.partner_user.user_id))
            partner_credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=partner_token,
            )
            self.assertEqual(
                get_current_delivery_partner(partner_credentials, self.db).partner_id,
                self.partner.partner_id,
            )
        assignments = list_partner_assignments(
            self.db,
            partner_id=self.partner.partner_id,
        )
        self.assertEqual([row.assignment_id for row in assignments], [assignment.assignment_id])
        detail = get_partner_assignment(
            self.db,
            partner_id=self.partner.partner_id,
            assignment_id=assignment.assignment_id,
        )
        self.assertEqual(detail.order_id, order.order_id)
        point = add_tracking_point(
            self.db,
            partner_id=self.partner.partner_id,
            user_id=self.partner_user.user_id,
            assignment_id=assignment.assignment_id,
            request=DeliveryTrackingCreate(
                latitude=Decimal("12.3456789"),
                longitude=Decimal("76.5432109"),
            ),
        )
        self.assertEqual(point.assignment_id, assignment.assignment_id)
        self.assertEqual(
            len(
                list_customer_order_tracking(
                    self.db,
                    customer_id=self.customer.customer_id,
                    order_id=order.order_id,
                )
            ),
            1,
        )
        with self.assertRaises(AssignmentNotFound):
            get_partner_assignment(
                self.db,
                partner_id=self.second_partner.partner_id,
                assignment_id=assignment.assignment_id,
            )
        with self.assertRaises(TrackingOrderNotFound):
            list_customer_order_tracking(
                self.db,
                customer_id=self.second_customer.customer_id,
                order_id=order.order_id,
            )
        with self.assertRaises(AssignmentNotFound):
            add_tracking_point(
                self.db,
                partner_id=self.second_partner.partner_id,
                user_id=self.second_partner_user.user_id,
                assignment_id=assignment.assignment_id,
                request=DeliveryTrackingCreate(
                    latitude=Decimal("0"),
                    longitude=Decimal("0"),
                ),
            )

        restaurant_review = create_restaurant_review(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            restaurant_id=self.restaurant.restaurant_id,
            order_id=order.order_id,
            rating=4,
            review_text="Good",
        )
        food_review = create_food_item_review(
            self.db,
            customer_id=self.customer.customer_id,
            user_id=self.customer_user.user_id,
            item_id=self.item.item_id,
            order_item_id=order.items[0].order_item_id,
            rating=3,
            review_text="Tasty",
        )
        self.assertEqual(
            len(
                list_restaurant_reviews(
                    self.db,
                    restaurant_id=self.restaurant.restaurant_id,
                    limit=20,
                    offset=0,
                )
            ),
            1,
        )
        self.assertEqual(
            len(
                list_food_item_reviews(
                    self.db,
                    item_id=self.item.item_id,
                    limit=20,
                    offset=0,
                )
            ),
            1,
        )
        with self.assertRaises(DuplicateReview):
            create_restaurant_review(
                self.db,
                customer_id=self.customer.customer_id,
                user_id=self.customer_user.user_id,
                restaurant_id=self.restaurant.restaurant_id,
                order_id=order.order_id,
                rating=5,
                review_text=None,
            )
        with self.assertRaises(DuplicateReview):
            create_food_item_review(
                self.db,
                customer_id=self.customer.customer_id,
                user_id=self.customer_user.user_id,
                item_id=self.item.item_id,
                order_item_id=order.items[0].order_item_id,
                rating=2,
                review_text=None,
            )
        with self.assertRaises(PurchaseNotFound):
            create_food_item_review(
                self.db,
                customer_id=self.second_customer.customer_id,
                user_id=self.second_customer_user.user_id,
                item_id=self.item.item_id,
                order_item_id=order.items[0].order_item_id,
                rating=5,
                review_text=None,
            )
        with self.assertRaises(ReviewNotFound):
            update_restaurant_review(
                self.db,
                customer_id=self.second_customer.customer_id,
                user_id=self.second_customer_user.user_id,
                restaurant_id=self.restaurant.restaurant_id,
                review_id=restaurant_review.review_id,
                update=ReviewUpdate(rating=1),
            )
        delete_restaurant_review(
            self.db,
            customer_id=self.customer.customer_id,
            restaurant_id=self.restaurant.restaurant_id,
            review_id=restaurant_review.review_id,
        )
        delete_food_item_review(
            self.db,
            customer_id=self.customer.customer_id,
            item_id=self.item.item_id,
            review_id=food_review.review_id,
        )
        self.assertIsNone(
            self.db.scalar(
                select(RestaurantReview.review_id).where(
                    RestaurantReview.review_id == restaurant_review.review_id
                )
            )
        )
        self.assertIsNone(
            self.db.scalar(
                select(FoodItemReview.review_id).where(
                    FoodItemReview.review_id == food_review.review_id
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
