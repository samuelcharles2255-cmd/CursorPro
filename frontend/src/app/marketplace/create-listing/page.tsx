"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  CheckCircle2,
  Upload,
  Plus,
  Trash2,
  DollarSign,
  MapPin,
  Sparkles,
  HelpCircle,
  Tag,
  ShieldCheck,
  Image as ImageIcon,
  X,
} from "lucide-react";
import { fetchCategories, createListing, uploadListingImage, FALLBACK_CATEGORIES } from "@/lib/api";
import { Category } from "@/types";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassInput } from "@/components/ui/GlassInput";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassSidebar } from "@/components/layout/GlassSidebar";
import { formatTZS } from "@/lib/utils";
import { useAuth } from "@/lib/auth";

export default function CreateListingPage() {
  const router = useRouter();
  const { token, loginAsDemo } = useAuth();
  const [categories, setCategories] = useState<Category[]>(FALLBACK_CATEGORIES);
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Form State
  const [title, setTitle] = useState("");
  const [categoryId, setCategoryId] = useState<number>(1);
  const [condition, setCondition] = useState("LIKE_NEW");
  const [price, setPrice] = useState("");
  const [isNegotiable, setIsNegotiable] = useState(true);
  const [region, setRegion] = useState("Dar es Salaam");
  const [district, setDistrict] = useState("Kinondoni");
  const [ward, setWard] = useState("Masaki");
  const [pickupAvailable, setPickupAvailable] = useState(true);
  const [deliveryAvailable, setDeliveryAvailable] = useState(true);
  const [description, setDescription] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  const [attributes, setAttributes] = useState<{ name: string; value: string }[]>([
    { name: "Brand / Model", value: "" },
    { name: "Warranty", value: "3 Months Tested" },
  ]);

  useEffect(() => {
    async function load() {
      const cats = await fetchCategories();
      if (cats.length > 0) {
        setCategories(cats);
        setCategoryId(cats[0].id);
      }
    }
    load();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const files = Array.from(e.target.files);
    setSelectedFiles((prev) => [...prev, ...files]);
    const newPreviews = files.map((f) => URL.createObjectURL(f));
    setPreviewUrls((prev) => [...prev, ...newPreviews]);
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
    setPreviewUrls((prev) => prev.filter((_, i) => i !== index));
  };

  const addAttribute = () => {
    setAttributes([...attributes, { name: "", value: "" }]);
  };

  const removeAttribute = (index: number) => {
    setAttributes(attributes.filter((_, i) => i !== index));
  };

  const updateAttribute = (index: number, field: "name" | "value", text: string) => {
    const updated = [...attributes];
    updated[index][field] = text;
    setAttributes(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg(null);

    let activeToken = token;
    if (!activeToken) {
      // Auto-connect demo merchant credentials if user creates listing without manual login
      try {
        await loginAsDemo("seller");
        activeToken = localStorage.getItem("atrium_token");
      } catch (e) {
        console.warn("Auto demo login error:", e);
      }
    }

    try {
      const payload = {
        title,
        category: categoryId,
        condition,
        price: parseFloat(price) || 0,
        is_negotiable: isNegotiable,
        region,
        district,
        ward,
        pickup_available: pickupAvailable,
        delivery_available: deliveryAvailable,
        description,
        attributes_data: attributes.filter((a) => a.name.trim() && a.value.trim()),
      };

      const result = await createListing(payload, activeToken || undefined);

      // Upload selected high-resolution images
      if (selectedFiles.length > 0 && activeToken && result?.id) {
        for (let i = 0; i < selectedFiles.length; i++) {
          try {
            await uploadListingImage(result.id, selectedFiles[i], i === 0, activeToken);
          } catch (uploadErr) {
            console.warn(`Image #${i + 1} upload notice:`, uploadErr);
          }
        }
      }

      setSuccessMsg("Your listing was published successfully to Atrium Marketplace!");
      setTimeout(() => {
        router.push(`/marketplace/listing/${result.slug || result.id}`);
      }, 1500);
    } catch (err: any) {
      console.warn("Listing creation error:", err);
      setErrorMsg(err.message || "Failed to publish listing. Please check form inputs.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
      <GlassSidebar />

      <main className="flex-1 space-y-8 min-w-0 max-w-3xl">
        {/* Header */}
        <div className="space-y-2">
          <Link
            href="/marketplace"
            className="text-xs text-zinc-400 hover:text-white flex items-center gap-1 mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Marketplace
          </Link>
          <div className="flex items-center gap-2">
            <GlassBadge variant="gold">Merchant Studio</GlassBadge>
            <span className="text-xs text-zinc-500">Step {currentStep} of 4</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-serif font-medium text-white">
            List an Item for Trade
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400">
            A simple, guided process designed for sellers. No technical knowledge required.
          </p>
        </div>

        {/* Wizard Progress Steps Bar */}
        <div className="grid grid-cols-4 gap-2">
          {[
            { num: 1, label: "Item Basics" },
            { num: 2, label: "Pricing & Handover" },
            { num: 3, label: "Details & Specs" },
            { num: 4, label: "Review & Publish" },
          ].map((s) => (
            <div
              key={s.num}
              onClick={() => s.num < currentStep && setCurrentStep(s.num)}
              className={`p-3 rounded-xl border text-xs transition-all cursor-pointer ${
                currentStep === s.num
                  ? "bg-gold-500/15 border-gold-500/40 text-gold-300 font-semibold shadow-gold-glow/10"
                  : currentStep > s.num
                  ? "bg-dark-850/60 border-white/[0.1] text-emerald-400"
                  : "bg-dark-900/40 border-white/[0.05] text-zinc-500"
              }`}
            >
              <div className="flex items-center gap-1.5">
                {currentStep > s.num ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <span className="w-4 h-4 rounded-full bg-white/[0.08] flex items-center justify-center text-[10px]">
                    {s.num}
                  </span>
                )}
                <span className="truncate hidden sm:inline">{s.label}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Error / Success Notifications */}
        {errorMsg && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            {errorMsg}
          </div>
        )}
        {successMsg && (
          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            {successMsg}
          </div>
        )}

        {/* Form Container */}
        <form onSubmit={handleSubmit} className="p-6 sm:p-8 rounded-3xl bg-dark-850/75 border border-white/[0.09] backdrop-blur-2xl shadow-glass-elevated space-y-6">
          {/* STEP 1: ITEM BASICS */}
          {currentStep === 1 && (
            <div className="space-y-5">
              <h3 className="text-base font-semibold text-white">Item Classification</h3>

              <GlassInput
                label="Listing Title *"
                placeholder="e.g. MacBook Pro 16 M3 Max (64GB RAM / 2TB SSD) Space Black"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />

              <div className="space-y-1.5">
                <label className="block text-xs font-medium uppercase tracking-wider text-zinc-400">
                  Department / Category *
                </label>
                <select
                  value={categoryId}
                  onChange={(e) => setCategoryId(Number(e.target.value))}
                  className="w-full bg-dark-900 border border-white/[0.09] rounded-xl px-4 py-2.5 text-sm text-zinc-200 focus:outline-none focus:border-gold-500/50"
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-medium uppercase tracking-wider text-zinc-400">
                  Item Condition *
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {[
                    { id: "NEW", label: "Brand New" },
                    { id: "LIKE_NEW", label: "Like New / Pristine" },
                    { id: "GOOD", label: "Good Working" },
                    { id: "REFURBISHED", label: "Refurbished" },
                  ].map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => setCondition(c.id)}
                      className={`p-3 rounded-xl border text-xs font-medium text-left transition-all ${
                        condition === c.id
                          ? "bg-gold-500/15 border-gold-500/40 text-gold-300 shadow-gold-glow/10"
                          : "bg-dark-900 border-white/[0.07] text-zinc-400 hover:text-white"
                      }`}
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Real Item Imagery & Photos */}
              <div className="space-y-2 pt-2">
                <div className="flex items-center justify-between">
                  <label className="block text-xs font-medium uppercase tracking-wider text-zinc-400">
                    Product Photography &amp; Assets
                  </label>
                  <span className="text-[11px] text-zinc-500">
                    {selectedFiles.length} photo{selectedFiles.length === 1 ? "" : "s"} attached
                  </span>
                </div>

                <div className="p-5 rounded-2xl bg-dark-900/60 border border-dashed border-white/[0.12] hover:border-gold-500/40 transition-colors text-center space-y-3">
                  <input
                    type="file"
                    id="listing-images-upload"
                    multiple
                    accept="image/*"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <label
                    htmlFor="listing-images-upload"
                    className="cursor-pointer inline-flex flex-col items-center gap-2"
                  >
                    <div className="w-10 h-10 rounded-xl bg-gold-500/15 border border-gold-500/30 flex items-center justify-center text-gold-300 mx-auto">
                      <ImageIcon className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-white hover:text-gold-300 transition-colors">
                        Click to upload product photographs
                      </p>
                      <p className="text-[11px] text-zinc-500 mt-0.5">
                        JPEG or PNG up to 10MB each. First uploaded photo serves as primary showcase cover.
                      </p>
                    </div>
                  </label>

                  {/* Thumbnail Previews */}
                  {previewUrls.length > 0 && (
                    <div className="grid grid-cols-3 sm:grid-cols-5 gap-2.5 pt-3 border-t border-white/[0.06]">
                      {previewUrls.map((url, idx) => (
                        <div key={idx} className="relative group rounded-xl overflow-hidden aspect-square border border-white/[0.1] bg-dark-950">
                          <img src={url} alt={`Preview ${idx + 1}`} className="w-full h-full object-cover" />
                          {idx === 0 && (
                            <span className="absolute bottom-1 left-1 px-1.5 py-0.5 rounded text-[8px] font-bold bg-gold-500 text-dark-950">
                              PRIMARY
                            </span>
                          )}
                          <button
                            type="button"
                            onClick={() => handleRemoveFile(idx)}
                            className="absolute top-1 right-1 p-1 rounded-full bg-dark-950/80 text-zinc-400 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-opacity"
                            title="Remove photo"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="pt-4 flex justify-end">
                <GlassButton
                  type="button"
                  variant="gold"
                  size="md"
                  onClick={() => {
                    if (!title.trim()) {
                      setErrorMsg("Please enter a listing title before proceeding.");
                      return;
                    }
                    setErrorMsg(null);
                    setCurrentStep(2);
                  }}
                >
                  Next: Pricing & Handover →
                </GlassButton>
              </div>
            </div>
          )}

          {/* STEP 2: PRICING & HANDOVER */}
          {currentStep === 2 && (
            <div className="space-y-5">
              <h3 className="text-base font-semibold text-white">Pricing & Logistics</h3>

              <div className="space-y-1.5">
                <GlassInput
                  label="Price in Tanzanian Shillings (TSh) *"
                  type="number"
                  placeholder="e.g. 7850000"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  required
                />
                {price && (
                  <p className="text-xs text-gold-400 font-sans font-semibold">
                    Preview: {formatTZS(price)}
                  </p>
                )}
              </div>

              <div className="p-4 rounded-2xl bg-dark-900/60 border border-white/[0.06] flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-white">Price is Negotiable (Inamaongezi)</p>
                  <p className="text-[11px] text-zinc-400">
                    Allow potential buyers to submit price offers for your review.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={isNegotiable}
                  onChange={(e) => setIsNegotiable(e.target.checked)}
                  className="w-4 h-4 rounded accent-gold-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs text-zinc-400">Region</label>
                  <input
                    type="text"
                    value={region}
                    onChange={(e) => setRegion(e.target.value)}
                    className="w-full bg-dark-900 border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-white"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs text-zinc-400">District</label>
                  <select
                    value={district}
                    onChange={(e) => setDistrict(e.target.value)}
                    className="w-full bg-dark-900 border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-white"
                  >
                    <option value="Kinondoni">Kinondoni</option>
                    <option value="Ilala">Ilala</option>
                    <option value="Temeke">Temeke</option>
                    <option value="Ubungo">Ubungo</option>
                    <option value="Kigamboni">Kigamboni</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs text-zinc-400">Ward / Area</label>
                  <input
                    type="text"
                    value={ward}
                    onChange={(e) => setWard(e.target.value)}
                    placeholder="e.g. Masaki, Kariakoo"
                    className="w-full bg-dark-900 border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <label className="p-3 rounded-xl bg-dark-900 border border-white/[0.06] flex items-center gap-2 cursor-pointer text-xs">
                  <input
                    type="checkbox"
                    checked={pickupAvailable}
                    onChange={(e) => setPickupAvailable(e.target.checked)}
                    className="accent-gold-500"
                  />
                  <span>Physical Pickup Available</span>
                </label>
                <label className="p-3 rounded-xl bg-dark-900 border border-white/[0.06] flex items-center gap-2 cursor-pointer text-xs">
                  <input
                    type="checkbox"
                    checked={deliveryAvailable}
                    onChange={(e) => setDeliveryAvailable(e.target.checked)}
                    className="accent-gold-500"
                  />
                  <span>Courier Delivery Available</span>
                </label>
              </div>

              <div className="pt-4 flex justify-between">
                <GlassButton
                  type="button"
                  variant="ghost"
                  size="md"
                  onClick={() => setCurrentStep(1)}
                >
                  ← Back
                </GlassButton>
                <GlassButton
                  type="button"
                  variant="gold"
                  size="md"
                  onClick={() => {
                    if (!price || Number(price) <= 0) {
                      setErrorMsg("Please enter a valid price in Tanzanian Shillings.");
                      return;
                    }
                    setErrorMsg(null);
                    setCurrentStep(3);
                  }}
                >
                  Next: Item Details →
                </GlassButton>
              </div>
            </div>
          )}

          {/* STEP 3: DETAILS & SPECS */}
          {currentStep === 3 && (
            <div className="space-y-5">
              <h3 className="text-base font-semibold text-white">Full Description & Specs</h3>

              <div className="space-y-1.5">
                <label className="block text-xs font-medium uppercase tracking-wider text-zinc-400">
                  Full Description & Inclusions *
                </label>
                <textarea
                  rows={4}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe included cables, original packaging, cosmetic state, and reason for sale..."
                  className="w-full bg-dark-900 border border-white/[0.09] rounded-xl p-3 text-xs text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:border-gold-500/50"
                  required
                />
              </div>

              {/* Dynamic Key-Value Attributes */}
              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-zinc-300">
                    Product Specifications (Optional)
                  </label>
                  <button
                    type="button"
                    onClick={addAttribute}
                    className="text-xs text-gold-400 hover:text-gold-300 flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    Add Specification
                  </button>
                </div>

                {attributes.map((attr, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <input
                      type="text"
                      placeholder="e.g. Storage"
                      value={attr.name}
                      onChange={(e) => updateAttribute(idx, "name", e.target.value)}
                      className="w-1/3 bg-dark-900 border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-white"
                    />
                    <input
                      type="text"
                      placeholder="e.g. 512GB SSD"
                      value={attr.value}
                      onChange={(e) => updateAttribute(idx, "value", e.target.value)}
                      className="flex-1 bg-dark-900 border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-white"
                    />
                    <button
                      type="button"
                      onClick={() => removeAttribute(idx)}
                      className="p-2 text-zinc-500 hover:text-rose-400"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>

              <div className="pt-4 flex justify-between">
                <GlassButton
                  type="button"
                  variant="ghost"
                  size="md"
                  onClick={() => setCurrentStep(2)}
                >
                  ← Back
                </GlassButton>
                <GlassButton
                  type="button"
                  variant="gold"
                  size="md"
                  onClick={() => {
                    if (!description.trim()) {
                      setErrorMsg("Please provide a description of the item.");
                      return;
                    }
                    setErrorMsg(null);
                    setCurrentStep(4);
                  }}
                >
                  Next: Final Review →
                </GlassButton>
              </div>
            </div>
          )}

          {/* STEP 4: REVIEW & PUBLISH */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <h3 className="text-base font-semibold text-white">Review Before Publishing</h3>

              <div className="p-5 rounded-2xl bg-dark-900/70 border border-white/[0.08] space-y-3 text-xs">
                <div className="flex justify-between border-b border-white/[0.05] pb-2">
                  <span className="text-zinc-400">Title:</span>
                  <span className="font-semibold text-white text-right max-w-xs">{title}</span>
                </div>
                <div className="flex justify-between border-b border-white/[0.05] pb-2">
                  <span className="text-zinc-400">Asking Price:</span>
                  <span className="font-bold text-market-400">{formatTZS(price)}</span>
                </div>
                <div className="flex justify-between border-b border-white/[0.05] pb-2">
                  <span className="text-zinc-400">Condition:</span>
                  <span className="text-white">{condition}</span>
                </div>
                <div className="flex justify-between border-b border-white/[0.05] pb-2">
                  <span className="text-zinc-400">Location:</span>
                  <span className="text-white">
                    {ward}, {district}, {region}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-400">Escrow Security:</span>
                  <span className="text-emerald-400 font-medium">Automatic Protection Enabled</span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-gold-500/10 border border-gold-500/20 text-xs text-gold-300 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 flex-shrink-0" />
                <span>
                  Once published, buyers can chat, make offers, or add to cart. You will receive notifications in your Seller Dashboard.
                </span>
              </div>

              <div className="pt-4 flex justify-between">
                <GlassButton
                  type="button"
                  variant="ghost"
                  size="md"
                  onClick={() => setCurrentStep(3)}
                >
                  ← Back
                </GlassButton>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="min-h-[48px] px-6 rounded-2xl bg-market-600 hover:bg-market-500 text-dark-950 font-bold text-xs inline-flex items-center gap-2 shadow-green-glow disabled:opacity-50 transition-all active:scale-98"
                >
                  {isSubmitting ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-dark-950 border-t-transparent rounded-full animate-spin" />
                      Publishing to Market...
                    </span>
                  ) : (
                    "Publish Listing to The City Marketplace"
                  )}
                </button>
              </div>
            </div>
          )}
        </form>
      </main>
    </div>
  );
}
