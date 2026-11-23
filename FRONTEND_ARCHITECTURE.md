# ATRIUM · Premium Next.js 15 Frontend Architecture

## Overview
A production-ready, ultra-premium frontend for **Atrium**, a dual-purpose platform combining an **Executive Career Hub (Jobs)** and a **Fine Trade Marketplace** with integrated **Market News & Intelligence**.

Built with **Next.js 15 (App Router)**, **TypeScript**, **Tailwind CSS**, and **Framer Motion**, following an aesthetic of *Quiet Luxury* (inspired by Linear, Arc, Raycast, and Stripe Dashboard).

---

## 1. Design System & Aesthetics
- **Color Palette**:
  - Backgrounds: `#0a0a0b` (Primary Dark), `#111113` (Surface), `#18181b` (Subtle Card Surface)
  - Accents: `#d4af37` (Muted Champagne Gold), `#e5c378` (Soft Gold), `#6366f1` (Quiet Indigo)
  - Text: `#ededed` (Soft White Primary), `#a1a1aa` (Muted Gray), `#71717a` (Dim Gray)
- **Glassmorphism**:
  - Consistent frosted blur (`backdrop-blur-xl`, `backdrop-blur-2xl`)
  - Sub-pixel borders (`border-white/[0.08]`, `border-gold-500/25`)
  - Soft inner ambient depth and elevation shadows (`shadow-glass-elevated`, `shadow-gold-glow`)
- **Typography**:
  - Geometric clean sans (`Inter`) paired with refined luxury serif accents (`Cormorant Garamond`)

---

## 2. Pages Implemented (In User-Requested Order)

| # | Route | Purpose & Key Features |
|---|-------|------------------------|
| 1 | `/` | **Base Homepage**: Dual gateway showcasing what users find on the platform: **Marketplace**, **Careers & Jobs**, and **Market Intelligence**, with dual-mode search and live statistics. |
| 2 | `/marketplace/category/[slug]` | **Category Page**: Dynamic subcategory pills, price range, condition filters (Brand New, Like New, Refurbished), sorting, and grid. |
| 3 | `/marketplace/search` | **Search Results**: Multi-faceted glass sidebar filter (department, Dar es Salaam districts, condition, min/max TZS), query highlight, and sorting. |
| 4 | `/marketplace/listing/[slug]` | **Product Details**: Image gallery preview, TZS pricing with negotiable badge, verified seller card, dynamic key-value attributes (RAM, storage, year, warranty), "Make Offer" modal, and "Direct Chat" modal. |
| 5 | `/marketplace/seller/[slug]` | **Seller Profile**: Verified Pro Merchant badge, trust rating (4.98), response time, follower toggle, active inventory grid, and client reviews. |
| 6 | `/auth/login` & `/auth/register` | **Auth Pages**: Glass cards with switchable Email/Password and Tanzanian Phone OTP (`+255`), role selectors (Merchant, Buyer, Job Seeker). |
| 7 | `/marketplace/create-listing` | **Create Listing**: Simple 4-step wizard for non-technical sellers (Basics -> Pricing & Location -> Specs -> Final Review & Publish to Django API). |
| 8 | `/marketplace/seller/dashboard` | **Seller Dashboard**: Advanced analytics with 4 metric cards (Gross Volume, Active Items, Views, Inquiries), 30-day SVG performance chart, and listing inventory management table (mark sold, renew, delete). |
| 9 | `/marketplace/messages` | **Messaging Interface**: Real-time glass chat split pane with buyer/seller threads, listing context header, quick counter-offer pills, and escrow guarantee. |
| 10 | `/marketplace/moderation` | **Admin/Moderation**: Listing review queue (Approve/Reject), risk scores, seller verification status, and safety metrics. |
| 11 | `/marketplace/cart` | **Cart & Checkout**: Slide-out/page bag summary, courier vs in-person pickup selection, M-Pesa/Tigo/Bank options, and escrow order confirmation. |
| 12 | `/jobs` & `/jobs/[id]` | **Careers Section**: Consumes 770+ active jobs from Django backend (`/api/jobs/`), skill pills, and application modal. |
| 13 | `/profile` | **Profile & Settings**: Account credentials, demo role switch (Seller <-> Buyer), and Tanzania PDPA 2022 data export. |

---

## 3. Django Backend API Consumption
The Next.js frontend is configured to consume Django REST Framework APIs via `process.env.NEXT_PUBLIC_API_URL`:

- **Listings API**: `GET /api/listings/`, `POST /api/listings/`, `GET /api/listings/<slug>/`, `POST /api/listings/<id>/upload_image/`
- **Categories API**: `GET /api/categories/`
- **Jobs API**: `GET /api/jobs/`, `GET /api/jobs/<id>/`
- **Auth API**: `POST /api/auth/login/`, `POST /api/auth/register/`, `POST /api/auth/verify-phone/`
- **Conversations API**: `GET /api/conversations/`, `POST /api/conversations/`

---

## 4. How to Run
1. **Start Django Backend**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
2. **Start Next.js Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) in your browser.
