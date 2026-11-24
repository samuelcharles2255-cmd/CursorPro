export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon: string;
  image: string | null;
  display_order: number;
  subcategories: Subcategory[];
  listings_count: number;
}

export interface Subcategory {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon: string;
  display_order: number;
}

export interface ListingAttribute {
  id?: number;
  name: string;
  value: string;
}

export interface ListingImage {
  id: number;
  image: string;
  is_primary: boolean;
  order: number;
  created_at: string;
}

export interface Listing {
  id: number;
  title: string;
  slug: string;
  description?: string;
  price: string | number;
  is_negotiable: boolean;
  category: number;
  category_name?: string;
  category_slug?: string;
  subcategory?: number | null;
  subcategory_name?: string | null;
  condition: "NEW" | "LIKE_NEW" | "GOOD" | "FAIR" | "REFURBISHED";
  status: "DRAFT" | "PENDING_REVIEW" | "ACTIVE" | "SOLD" | "REJECTED" | "EXPIRED";
  region: string;
  district: string;
  ward?: string;
  street_address?: string;
  pickup_available?: boolean;
  delivery_available?: boolean;
  primary_image_url?: string | null;
  seller_id?: number;
  seller_name?: string;
  seller_username?: string;
  seller_phone?: string;
  views_count?: number;
  images?: ListingImage[];
  attributes?: ListingAttribute[];
  created_at: string;
  updated_at?: string;
  expires_at?: string;
}

export interface Job {
  id: number;
  title: string;
  company?: any;
  company_name: string;
  company_logo?: string | null;
  location: string;
  country: string;
  employment_type: string;
  experience_level?: string;
  is_remote?: boolean;
  salary_min?: string | number | null;
  salary_max?: string | number | null;
  salary_currency?: string;
  posted_at: string;
  expires_at?: string | null;
  description?: string;
  requirements?: string;
  benefits?: string;
  how_to_apply?: string;
  application_url?: string;
  source_url?: string;
  is_active?: boolean;
  skills?: { id: number; name: string }[];
}

export interface User {
  id: number;
  email: string;
  username: string;
  name?: string;
  phone_number?: string;
  is_seller?: boolean;
  is_phone_verified?: boolean;
  avatar?: string;
}

export interface Conversation {
  id: number;
  listing_id?: number;
  listing_title?: string;
  listing_slug?: string;
  listing_price?: string | number;
  listing_image?: string | null;
  listing?: {
    id: number;
    title: string;
    slug?: string;
    price: string | number;
    primary_image_url?: string | null;
  };
  other_participant?: {
    id: number;
    username: string;
    name?: string;
    role?: string;
  };
  buyer_id?: number;
  buyer_username?: string;
  seller_id?: number;
  seller_username?: string;
  last_message?: {
    id: number;
    sender_id: number;
    content: string;
    created_at: string;
    is_read?: boolean;
  };
  unread_count: number;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  sender_id: number;
  sender_username?: string;
  content: string;
  created_at: string;
  is_read: boolean;
}

export interface OrderItem {
  id?: number;
  listing?: number | null;
  listing_id?: number;
  title: string;
  unit_price?: number | string;
  price?: number;
  quantity: number;
  subtotal?: number | string;
  image?: string;
}

export interface Order {
  id: number;
  order_number: string;
  buyer?: number | null;
  buyer_name: string;
  buyer_phone: string;
  buyer_email?: string;
  delivery_method: "courier" | "pickup";
  delivery_address?: string;
  delivery_district?: string;
  delivery_region?: string;
  payment_method: "mpesa" | "tigo" | "airtel" | "bank";
  status: "PENDING_PAYMENT" | "ESCROW_LOCKED" | "DISPATCHED" | "DELIVERED" | "RELEASED" | "CANCELLED";
  items_total: number | string;
  delivery_fee: number | string;
  total_amount: number | string;
  notes?: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface JobApplication {
  id: number;
  job: number;
  job_title: string;
  company_name: string;
  company_logo?: string;
  location?: string;
  full_name: string;
  email: string;
  phone: string;
  cover_letter?: string;
  resume_url?: string;
  status: "SUBMITTED" | "UNDER_REVIEW" | "INTERVIEW_SCHEDULED" | "OFFERED" | "REJECTED";
  created_at: string;
  updated_at: string;
}

export interface SavedJob {
  id: number;
  job: number;
  job_details?: Job;
  created_at: string;
}
