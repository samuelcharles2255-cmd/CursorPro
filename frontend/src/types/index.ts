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
  company?: number;
  company_name: string;
  company_logo?: string | null;
  location: string;
  country: string;
  employment_type: string;
  salary_min?: string | number | null;
  salary_max?: string | number | null;
  salary_currency?: string;
  posted_at: string;
  expires_at?: string | null;
  description?: string;
  skills?: { id: number; name: string }[];
}

export interface User {
  id: number;
  email: string;
  username: string;
  name?: string;
  phone_number?: string;
  is_seller?: boolean;
  avatar?: string;
}

export interface Conversation {
  id: number;
  listing?: {
    id: number;
    title: string;
    price: string | number;
    primary_image_url?: string | null;
  };
  other_participant: {
    id: number;
    username: string;
    name?: string;
  };
  last_message?: {
    id: number;
    sender_id: number;
    content: string;
    created_at: string;
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
  id: number;
  listing_id: number;
  title: string;
  price: number;
  image?: string;
  quantity: number;
}
