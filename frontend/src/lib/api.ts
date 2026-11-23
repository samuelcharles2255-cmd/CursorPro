import { Category, Listing, Job, User, Conversation, ChatMessage } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// Fallback high-ticket listings for offline/prerender assurance
export const FALLBACK_LISTINGS: Listing[] = [
  {
    id: 1,
    title: "MacBook Pro 16\" M3 Max (64GB RAM / 2TB SSD) Space Black",
    slug: "macbook-pro-16-m3-max-space-black",
    description: "Pristine condition flagship Apple MacBook Pro M3 Max. Liquid Retina XDR display, 16-core CPU, 40-core GPU. Complete with original MagSafe charger, braided cable, and AppleCare+ warranty until late 2026. Perfect for AI engineering and 8K video pipelines.",
    price: 7850000,
    is_negotiable: true,
    category: 1,
    category_name: "Electronics & Gadgets",
    category_slug: "electronics",
    condition: "LIKE_NEW",
    status: "ACTIVE",
    region: "Dar es Salaam",
    district: "Kinondoni",
    ward: "Masaki",
    primary_image_url: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
    seller_id: 1,
    seller_name: "Lumina Luxury Tech",
    seller_phone: "+255755123456",
    views_count: 342,
    attributes: [
      { name: "Processor", value: "Apple M3 Max 16-Core" },
      { name: "RAM", value: "64GB Unified Memory" },
      { name: "Storage", value: "2TB PCIe SSD" },
      { name: "Color", value: "Space Black" },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: 2,
    title: "Rolex Submariner Date 41mm 'Kermit' Oystersteel (Ref. 126610LV)",
    slug: "rolex-submariner-date-41mm-kermit",
    description: "Original Rolex Submariner Date 41mm green Cerachrom bezel with black dial. Complete with original presentation green box, chronometer certificate card, tags, and extra links. Verified authentic with papers. Available for in-person jeweler escrow in Dar es Salaam.",
    price: 38500000,
    is_negotiable: false,
    category: 2,
    category_name: "Luxury & Fashion",
    category_slug: "luxury-fashion",
    condition: "NEW",
    status: "ACTIVE",
    region: "Dar es Salaam",
    district: "Kinondoni",
    ward: "Oysterbay",
    primary_image_url: "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=1200&q=80",
    seller_id: 1,
    seller_name: "Lumina Luxury Tech",
    seller_phone: "+255755123456",
    views_count: 819,
    attributes: [
      { name: "Brand", value: "Rolex" },
      { name: "Model", value: "Submariner Date 126610LV" },
      { name: "Case Size", value: "41mm" },
      { name: "Bezel", value: "Green Cerachrom" },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: 3,
    title: "Sony Alpha A7R V Full-Frame Mirrorless Camera + GM 24-70mm f/2.8 II",
    slug: "sony-alpha-a7r-v-gm-lens-bundle",
    description: "61.0 MP full-frame Exmor R BSI CMOS sensor with dedicated AI processing unit. Exceptional autofocus tracking, 8K video recording, and 8-stop image stabilization. Bundled with Sony FE 24-70mm F2.8 GM II lens and dual Lexar CFexpress Type A cards.",
    price: 11200000,
    is_negotiable: true,
    category: 1,
    category_name: "Electronics & Gadgets",
    category_slug: "electronics",
    condition: "LIKE_NEW",
    status: "ACTIVE",
    region: "Dar es Salaam",
    district: "Ilala",
    ward: "Kariakoo",
    primary_image_url: "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=1200&q=80",
    seller_id: 1,
    seller_name: "Lumina Luxury Tech",
    seller_phone: "+255755123456",
    views_count: 421,
    attributes: [
      { name: "Sensor", value: "61MP Full-Frame" },
      { name: "Lens", value: "Sony FE 24-70mm f/2.8 GM II" },
      { name: "Video", value: "8K 24p / 4K 60p" },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: 4,
    title: "Range Rover Autobiography P530 V8 Long Wheelbase (2023)",
    slug: "range-rover-autobiography-p530-v8-2023",
    description: "Santorini Black with Perlino Semi-Aniline executive rear leather seating. Twin-turbocharged 4.4L V8 engine generating 523 HP. Meridian Signature 1600W Sound System, active noise cancellation, rear-wheel steering, and air suspension. Clean local registration with low mileage.",
    price: 520000000,
    is_negotiable: true,
    category: 3,
    category_name: "Vehicles & Automotive",
    category_slug: "automotive",
    condition: "LIKE_NEW",
    status: "ACTIVE",
    region: "Dar es Salaam",
    district: "Kinondoni",
    ward: "Masaki",
    primary_image_url: "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=80",
    seller_id: 1,
    seller_name: "Lumina Luxury Tech",
    seller_phone: "+255755123456",
    views_count: 1403,
    attributes: [
      { name: "Year", value: "2023" },
      { name: "Engine", value: "4.4L Twin-Turbo V8" },
      { name: "Mileage", value: "14,200 km" },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: 5,
    title: "Executive Waterfront Penthouse - 4 Bedroom with Ocean Terrace",
    slug: "executive-waterfront-penthouse-msasani",
    description: "Panoramic Indian Ocean horizon views. 480 sq meters of architectural luxury with double-height ceiling living salon, Poggenpohl kitchen with Miele appliances, private plunge pool on terrace, and 24/7 biometric security with 3 underground parking slots.",
    price: 1450000000,
    is_negotiable: true,
    category: 4,
    category_name: "Real Estate & Living",
    category_slug: "real-estate",
    condition: "NEW",
    status: "ACTIVE",
    region: "Dar es Salaam",
    district: "Kinondoni",
    ward: "Msasani",
    primary_image_url: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
    seller_id: 1,
    seller_name: "Lumina Luxury Tech",
    seller_phone: "+255755123456",
    views_count: 2190,
    attributes: [
      { name: "Bedrooms", value: "4 Ensuite" },
      { name: "Floor Area", value: "480 m²" },
      { name: "Security", value: "24/7 Biometric & Guarded" },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: 6,
    title: "Enterprise Cloud Architecture & High-Scale Design Advisory",
    slug: "enterprise-cloud-architecture-design-advisory",
    description: "Comprehensive fractional CTO and principal cloud architect advisory for fintechs, marketplaces, and high-concurrency systems. Architecture reviews, SOC2/ISO compliance hardening, Kubernetes orchestration, and database scaling.",
    price: 9500000,
    is_negotiable: false,
    category: 5,
    category_name: "Services & Consultancies",
    category_slug: "services",
    condition: "NEW",
    status: "ACTIVE",
    region: "Dar es Salaam",
    district: "Ilala",
    ward: "Posta / Kisutu",
    primary_image_url: "https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=1200&q=80",
    seller_id: 1,
    seller_name: "Lumina Luxury Tech",
    seller_phone: "+255755123456",
    views_count: 512,
    attributes: [
      { name: "Advisory Type", value: "High-Scale Cloud & Distributed Systems" },
      { name: "Engagement", value: "Monthly Executive Retainer" },
    ],
    created_at: new Date().toISOString(),
  },
];

export const FALLBACK_CATEGORIES: Category[] = [
  {
    id: 1,
    name: "Electronics & Gadgets",
    slug: "electronics",
    description: "High-performance computing, flagship smartphones, and pro audio gear.",
    icon: "smartphone",
    image: "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80",
    display_order: 1,
    listings_count: 2,
    subcategories: [
      { id: 11, name: "Smartphones", slug: "smartphones", description: "", icon: "", display_order: 1 },
      { id: 12, name: "Laptops & MacBooks", slug: "laptops", description: "", icon: "", display_order: 2 },
      { id: 13, name: "Audio & Headphones", slug: "audio", description: "", icon: "", display_order: 3 },
      { id: 14, name: "Cameras & Drones", slug: "cameras", description: "", icon: "", display_order: 4 },
    ],
  },
  {
    id: 2,
    name: "Luxury & Fashion",
    slug: "luxury-fashion",
    description: "Designer timepieces, bespoke apparel, leather goods, and fine jewelry.",
    icon: "watch",
    image: "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
    display_order: 2,
    listings_count: 1,
    subcategories: [
      { id: 21, name: "Swiss Watches", slug: "watches", description: "", icon: "", display_order: 1 },
      { id: 22, name: "Designer Footwear", slug: "footwear", description: "", icon: "", display_order: 2 },
      { id: 23, name: "Leather Bags", slug: "bags", description: "", icon: "", display_order: 3 },
    ],
  },
  {
    id: 3,
    name: "Vehicles & Automotive",
    slug: "automotive",
    description: "Prestige SUVs, luxury sedans, electric vehicles, and verified classics.",
    icon: "car",
    image: "https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=800&q=80",
    display_order: 3,
    listings_count: 1,
    subcategories: [
      { id: 31, name: "SUVs & 4x4", slug: "suvs", description: "", icon: "", display_order: 1 },
      { id: 32, name: "Luxury Sedans", slug: "sedans", description: "", icon: "", display_order: 2 },
      { id: 33, name: "Electric Vehicles", slug: "evs", description: "", icon: "", display_order: 3 },
    ],
  },
  {
    id: 4,
    name: "Real Estate & Living",
    slug: "real-estate",
    description: "Prime residential penthouses, executive apartments, and architectural villas.",
    icon: "home",
    image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
    display_order: 4,
    listings_count: 1,
    subcategories: [
      { id: 41, name: "Villas & Mansions", slug: "villas", description: "", icon: "", display_order: 1 },
      { id: 42, name: "Serviced Penthouses", slug: "penthouses", description: "", icon: "", display_order: 2 },
      { id: 43, name: "Commercial Spaces", slug: "commercial", description: "", icon: "", display_order: 3 },
    ],
  },
  {
    id: 5,
    name: "Services & Consultancies",
    slug: "services",
    description: "High-end product design, cloud architecture, and corporate advisory.",
    icon: "briefcase",
    image: "https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=800&q=80",
    display_order: 5,
    listings_count: 1,
    subcategories: [
      { id: 51, name: "UI/UX & Product Design", slug: "design", description: "", icon: "", display_order: 1 },
      { id: 52, name: "Cloud Architecture", slug: "cloud", description: "", icon: "", display_order: 2 },
      { id: 53, name: "Executive Retainers", slug: "retainers", description: "", icon: "", display_order: 3 },
    ],
  },
];

export async function fetchListings(params: Record<string, string | number | undefined> = {}): Promise<{ count: number; results: Listing[] }> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, val]) => {
    if (val !== undefined && val !== "") query.set(key, String(val));
  });

  try {
    const res = await fetch(`${API_BASE}/api/listings/?${query.toString()}`, {
      next: { revalidate: 30 },
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    if (Array.isArray(data)) {
      return { count: data.length, results: data };
    }
    return { count: data.count || (data.results ? data.results.length : 0), results: data.results || [] };
  } catch (err) {
    console.warn("Using fallback listings:", err);
    let filtered = [...FALLBACK_LISTINGS];
    if (params.search) {
      const q = String(params.search).toLowerCase();
      filtered = filtered.filter((i) => i.title.toLowerCase().includes(q) || i.description?.toLowerCase().includes(q));
    }
    if (params.category_slug) {
      filtered = filtered.filter((i) => i.category_slug === params.category_slug);
    }
    return { count: filtered.length, results: filtered };
  }
}

export async function fetchListingBySlug(slug: string): Promise<Listing | null> {
  try {
    // Check API list by slug or detail
    const res = await fetch(`${API_BASE}/api/listings/?slug=${slug}`, { next: { revalidate: 15 } });
    if (res.ok) {
      const data = await res.json();
      const item = Array.isArray(data) ? data[0] : (data.results && data.results[0]);
      if (item) return item;
    }
  } catch (e) {
    console.warn("fetchListingBySlug API error:", e);
  }
  const match = FALLBACK_LISTINGS.find((i) => i.slug === slug || String(i.id) === slug);
  return match || null;
}

export async function fetchCategories(): Promise<Category[]> {
  try {
    const res = await fetch(`${API_BASE}/api/categories/`, { next: { revalidate: 60 } });
    if (res.ok) {
      const data = await res.json();
      const list = Array.isArray(data) ? data : data.results;
      if (list && list.length > 0) return list;
    }
  } catch (e) {
    console.warn("fetchCategories API error:", e);
  }
  return FALLBACK_CATEGORIES;
}

export async function fetchJobs(params: Record<string, string | number | undefined> = {}): Promise<Job[]> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, val]) => {
    if (val !== undefined && val !== "") query.set(key, String(val));
  });

  try {
    const res = await fetch(`${API_BASE}/api/jobs/?${query.toString()}`, {
      next: { revalidate: 60 },
    });
    if (res.ok) {
      const data = await res.json();
      return Array.isArray(data) ? data : (data.results || []);
    }
  } catch (e) {
    console.warn("fetchJobs API error:", e);
  }
  return [];
}

export async function fetchJobById(id: string | number): Promise<Job | null> {
  try {
    const res = await fetch(`${API_BASE}/api/jobs/${id}/`, { next: { revalidate: 60 } });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    console.warn("fetchJobById API error:", e);
  }
  return null;
}

export async function createListing(data: any, token?: string): Promise<Listing> {
  const res = await fetch(`${API_BASE}/api/listings/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(JSON.stringify(errorData) || `Failed to create listing: ${res.status}`);
  }
  return await res.json();
}

export async function uploadListingImage(listingId: number, file: File, isPrimary: boolean, token?: string) {
  const formData = new FormData();
  formData.append("image", file);
  formData.append("is_primary", String(isPrimary));
  formData.append("order", "0");

  const res = await fetch(`${API_BASE}/api/listings/${listingId}/upload_image/`, {
    method: "POST",
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: formData,
  });
  return await res.json();
}
