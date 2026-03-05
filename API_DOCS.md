# Crunch API Reference
Updated: 2026-03-06  
Stack: Django REST Framework + JWT (SimpleJWT)  
Base URL (local dev): `http://localhost:8000` – all endpoints are under `/api/` unless noted.

## Conventions
- **Auth**: `Authorization: Bearer <access_token>` for protected routes.  
  - Get tokens via `POST /api/token/` (SimpleJWT username/password) or the OTP/signup flows (`/api/auth/...`), all of which return `access` and `refresh`.
- **Content type**: `application/json` unless uploading images.
- **Pagination**: Page-number style. Query params: `page`, `page_size` (defaults noted per endpoint; capped at 50 or 100 depending on view).
- **Rate limits**: OTP flows are throttled to `3` requests per minute (`otp_requests` scope).

## Authentication & User
| Method | Path | Auth | Purpose / Body |
| --- | --- | --- | --- |
| POST | `/api/token/` | — | Standard JWT login (`username`, `password`). |
| POST | `/api/token/refresh/` | — | Refresh access token (`refresh`). |
| POST | `/api/auth/admin-login/` | — | Admin/staff password login. Body: `username`, `password`. Returns `role`, `access`, `refresh`. |
| POST | `/api/auth/create-staff/` | Admin | Create staff user. Body: `username`, `password`, `phone_number` (optional). |
| POST | `/api/auth/register/` | — | Request OTP for signup. Body: `phone_number`, `name`, `email` (optional). |
| POST | `/api/auth/resend-otp/` | — | Resend signup/login OTP. Body: `phone_number`. |
| POST | `/api/auth/verify-otp/` | — | Verify OTP for signup/login. Body: `phone_number`, `otp`, optional `name`, `email`. Returns tokens + role. |
| POST | `/api/auth/login-otp/` | — | Request OTP for login. Body: `phone_number`. |
| GET/PATCH | `/api/auth/profile/` | User | View/update own profile. Fields: `name`, `email`. `phone_number` & `role` are read-only. |
| GET/POST | `/api/auth/addresses/` | User | List or create addresses. Create fields: `address_type` (`Home`/`Work`/`Other`), `complete_address`, `landmark`, `pincode`, `latitude`, `longitude`, `is_default`. |
| GET/PATCH/DELETE | `/api/auth/addresses/<id>/` | User | Retrieve/update/delete own address. |
| GET | `/api/auth/verify-session/` | User | Quick token check; returns `authenticated`, `user_id`, `username`. |
| POST | `/api/auth/logout/` | User | Blacklist a refresh token. Body: `refresh`. |

### Example: Admin login → authorized request
```bash
curl -X POST http://localhost:8000/api/auth/admin-login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret"}'
# Use the returned access token:
curl http://localhost:8000/api/inventory/categories/ \
  -H "Authorization: Bearer <access>"
```

## Inventory (Menu & Categories)
Base: `/api/inventory/`

**Categories**
| Method | Path | Auth | Notes |
| --- | --- | --- | --- |
| GET | `public/categories/` | — | All categories, no pagination. |
| GET/POST | `categories/` | GET: public; POST: Admin/Staff | List (paginated, default page_size=12) or create category (`name`, `image`). |
| GET/PATCH/DELETE | `categories/<id>/` | GET: public; write: Admin/Staff | Returns/updates/deletes a category. |

**Menu items**
| Method | Path | Auth | Query / Body |
| --- | --- | --- | --- |
| GET | `public/menu-items/` | — | No pagination. Filters: `search`, `category`, `section`, `diet` (`VEG`/`NON-VEG`). Only `is_available=True` items. |
| GET/POST | `admin/menu-items/` | Admin/Staff | Paginated (page_size=12). Filters: `search`, `category`, `section`. POST fields: `category`, `section`, `name`, `description`, `image`, `dietary_preference`, `actual_price`, `offer_price`, `quantity`, `is_available`. Section limits enforced (e.g., `BEST SELLER` max 8, `BANNER` max 4, `COMBO MENU` 9, `TODAYS SPECIAL` 6). |
| GET/PATCH/DELETE | `admin/menu-items/<id>/` | GET: public; write: Admin/Staff | Retrieve/update/delete menu item. |

## Orders & Cart
Base: `/api/orders/`

| Method | Path | Auth | Purpose / Body |
| --- | --- | --- | --- |
| POST | `cart/merge/` | User | Replace server cart with frontend items. Body: `items: [{item_id, quantity}]`. Clears existing cart, then recreates. |
| POST | `place-order/` | User | Create order from current cart. Body: `address_id` (required), `payment_method` (default `COD`). Computes totals from cart; empties cart after success. |
| GET | `history/` | User | List own orders (newest first). Includes items and delivery address. |

Order item pricing uses `offer_price` when present, else `actual_price`. Payment status starts `PENDING`; order status starts `PLACED`.

## Bookings (Table Reservations)
Base: `/api/bookings/`

| Method | Path | Auth | Notes |
| --- | --- | --- | --- |
| POST | `create/` | — | Create a booking. Fields: `full_name`, `phone`, `email` (optional), `date`, `time`, `guests`, `notes` (optional). Rejects past dates/times. |
| GET | `all/` | Admin/Staff | Paginated (page_size=12, max 50). Filters: `search` across `full_name`, `phone`, `email`. Returns paging metadata. |

## Contact
Base: `/api/`

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `contact/` | — | Submit contact form (`full_name`, `email`, `subject`, `message`). |
| GET | `admin/contacts/` | Admin/Staff | Paginated (page_size=12). Search `full_name`/`email`. |
| GET | `admin/contacts/<id>/` | Admin/Staff | Retrieve single message. |
| DELETE | `admin/contacts/<id>/delete/` | Superadmin | Delete message. |
| POST | `admin/contacts/<id>/reply/` | Admin/Staff | Body: `reply_message`. Sends email reply and stores copy. |

## Banners
Base: `/api/banners/`

| Method | Path | Auth | Notes |
| --- | --- | --- | --- |
| GET | `all/` | — | List active banners (ordered newest first). |
| POST | `add/` | Admin | Create banner. Fields: `desktop_image`, `mobile_image`, `headline`, `description`, `button_label`, `link_url`. |
| PATCH/PUT | `edit/<id>/` | Admin | Update banner. |
| DELETE | `delete/<id>/` | Admin | Delete banner. |

## Site Settings
Base: `/api/site-settings/`

| Method | Path | Auth | Body |
| --- | --- | --- | --- |
| GET | `info/` | — | Returns singleton settings: `appName`, `email`, `phone`, `address`, `type_address`, `latitude`, `longitude`, `deliveryRadius`, `footerDescription`, `workingHours` `{weekdays,sunday}`, `socials` `{instagram,facebook,twitter,whatsapp}`. |
| PUT/PATCH | `info/` | Admin/Staff | Same fields as above; partial updates allowed. |

## Additional Notes
- **Media**: Image fields (`image`, `desktop_image`, `mobile_image`, `category.image`) expect multipart uploads; ensure `MEDIA_URL=/media/`.
- **Roles**: Custom roles (`admin`, `staff`, `user`) live on `accounts.User`. Permissions use `IsAdminUser` (admin or superuser) and `IsAdminOrStaff` (admin/staff/superuser).
- **Totals**: Cart and order totals are computed server-side; clients should not send price fields when placing orders.
- **Debug**: When `DEBUG=True`, media is served at `/media/` via Django static helper. In production, serve media via a proper file server/CDN.
