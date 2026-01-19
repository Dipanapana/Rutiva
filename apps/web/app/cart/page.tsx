'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import {
  ShoppingCart,
  Trash2,
  BookOpen,
  CreditCard,
  Tag,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cartApi } from '@/lib/api';
import { useCartStore, useAuthStore } from '@/lib/store';
import { formatPrice, getSubjectColor } from '@/lib/utils';

export default function CartPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();
  const { items, totalZar, setCart, clearCart } = useCartStore();
  const [promoCode, setPromoCode] = useState('');
  const [promoError, setPromoError] = useState<string | null>(null);
  const [selectedPayment, setSelectedPayment] = useState<string>('payfast');

  const { data: cartData, isLoading } = useQuery({
    queryKey: ['cart'],
    queryFn: () => cartApi.get(),
    enabled: isAuthenticated,
    onSuccess: (data: any) => {
      setCart(data.data.items, data.data.total_zar);
    },
  });

  const removeItemMutation = useMutation({
    mutationFn: (itemId: string) => cartApi.removeItem(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  const applyPromoMutation = useMutation({
    mutationFn: (code: string) => cartApi.applyPromo(code),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      setPromoError(null);
    },
    onError: (error: any) => {
      setPromoError(error.response?.data?.detail || 'Invalid promo code');
    },
  });

  const checkoutMutation = useMutation({
    mutationFn: (provider: string) => cartApi.checkout(provider),
    onSuccess: (data: any) => {
      // Redirect to payment URL
      if (data.data.payment_url) {
        window.location.href = data.data.payment_url;
      }
    },
  });

  const handleRemoveItem = (itemId: string) => {
    removeItemMutation.mutate(itemId);
  };

  const handleApplyPromo = () => {
    if (promoCode.trim()) {
      applyPromoMutation.mutate(promoCode.trim());
    }
  };

  const handleCheckout = () => {
    if (!isAuthenticated) {
      router.push('/login?redirect=/cart');
      return;
    }
    checkoutMutation.mutate(selectedPayment);
  };

  const cartItems = cartData?.data?.items || items;
  const cartTotal = cartData?.data?.total_zar || totalZar;
  const discount = cartData?.data?.discount_zar || 0;
  const subtotal = cartData?.data?.subtotal_zar || cartTotal;

  return (
    <>
      <Header />
      <main className="min-h-screen bg-gray-50">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <h1 className="mb-8 text-3xl font-bold text-gray-900">Your Cart</h1>

          {isLoading ? (
            <div className="animate-pulse space-y-4">
              {[...Array(2)].map((_, i) => (
                <div key={i} className="h-32 rounded-2xl bg-gray-200" />
              ))}
            </div>
          ) : cartItems.length === 0 ? (
            <div className="rounded-2xl bg-white p-12 text-center shadow-sm">
              <ShoppingCart className="mx-auto h-16 w-16 text-gray-400" />
              <h2 className="mt-4 text-xl font-semibold text-gray-900">
                Your cart is empty
              </h2>
              <p className="mt-2 text-gray-500">
                Browse our study guides and add some to your cart.
              </p>
              <Link href="/shop" className="mt-6 inline-block">
                <Button size="lg">Browse Study Guides</Button>
              </Link>
            </div>
          ) : (
            <div className="lg:grid lg:grid-cols-12 lg:gap-8">
              {/* Cart Items */}
              <div className="lg:col-span-7">
                <div className="space-y-4">
                  {cartItems.map((item: any, index: number) => {
                    const product = item.product || item.bundle;
                    const isBundle = !!item.bundle_id;

                    return (
                      <motion.div
                        key={item.id}
                        className="flex gap-4 rounded-2xl bg-white p-4 shadow-sm"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        {/* Thumbnail */}
                        <div className="relative h-24 w-24 flex-shrink-0 rounded-lg bg-gray-100 overflow-hidden">
                          {product?.thumbnail_url ? (
                            <img
                              src={product.thumbnail_url}
                              alt={product.title}
                              className="h-full w-full object-cover"
                            />
                          ) : (
                            <div className="flex h-full w-full items-center justify-center bg-primary-100">
                              <BookOpen className="h-8 w-8 text-primary-600" />
                            </div>
                          )}
                        </div>

                        {/* Details */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between">
                            <div>
                              {isBundle && (
                                <span className="inline-block mb-1 rounded-full bg-secondary-100 px-2 py-0.5 text-xs font-medium text-secondary-700">
                                  Bundle
                                </span>
                              )}
                              <h3 className="font-semibold text-gray-900 line-clamp-2">
                                {product?.title}
                              </h3>
                              {!isBundle && product?.subject && (
                                <p className="mt-1 text-sm text-gray-500">
                                  {product.subject.name} | Grade {product.grade} | Term{' '}
                                  {product.term}
                                </p>
                              )}
                            </div>
                            <button
                              onClick={() => handleRemoveItem(item.id)}
                              className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                            >
                              <Trash2 className="h-5 w-5" />
                            </button>
                          </div>
                          <div className="mt-2 text-lg font-bold text-gray-900">
                            {formatPrice(item.price_zar)}
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>

              {/* Order Summary */}
              <div className="mt-8 lg:col-span-5 lg:mt-0">
                <div className="sticky top-24 rounded-2xl bg-white p-6 shadow-sm">
                  <h2 className="text-lg font-semibold text-gray-900">Order Summary</h2>

                  {/* Promo Code */}
                  <div className="mt-4">
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Tag className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                        <Input
                          value={promoCode}
                          onChange={(e) => setPromoCode(e.target.value)}
                          placeholder="Promo code"
                          className="pl-10"
                        />
                      </div>
                      <Button
                        variant="outline"
                        onClick={handleApplyPromo}
                        isLoading={applyPromoMutation.isPending}
                      >
                        Apply
                      </Button>
                    </div>
                    {promoError && (
                      <p className="mt-1 text-sm text-red-500">{promoError}</p>
                    )}
                  </div>

                  {/* Totals */}
                  <div className="mt-6 space-y-3 border-t border-gray-100 pt-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Subtotal</span>
                      <span className="font-medium">{formatPrice(subtotal)}</span>
                    </div>
                    {discount > 0 && (
                      <div className="flex justify-between text-sm text-green-600">
                        <span>Discount</span>
                        <span>-{formatPrice(discount)}</span>
                      </div>
                    )}
                    <div className="flex justify-between border-t border-gray-100 pt-3">
                      <span className="text-lg font-semibold">Total</span>
                      <span className="text-lg font-bold text-primary-600">
                        {formatPrice(cartTotal)}
                      </span>
                    </div>
                  </div>

                  {/* Payment Methods */}
                  <div className="mt-6">
                    <h3 className="text-sm font-medium text-gray-700 mb-3">
                      Payment Method
                    </h3>
                    <div className="space-y-2">
                      {[
                        { id: 'payfast', name: 'PayFast', desc: 'Cards, EFT, SnapScan' },
                        { id: 'yoco', name: 'Yoco', desc: 'Credit/Debit Card' },
                      ].map((method) => (
                        <label
                          key={method.id}
                          className={`flex cursor-pointer items-center rounded-lg border-2 p-3 transition-colors ${
                            selectedPayment === method.id
                              ? 'border-primary-500 bg-primary-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <input
                            type="radio"
                            name="payment"
                            value={method.id}
                            checked={selectedPayment === method.id}
                            onChange={(e) => setSelectedPayment(e.target.value)}
                            className="h-4 w-4 text-primary-600"
                          />
                          <div className="ml-3">
                            <span className="font-medium text-gray-900">
                              {method.name}
                            </span>
                            <span className="ml-2 text-sm text-gray-500">
                              {method.desc}
                            </span>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Checkout Button */}
                  <Button
                    className="mt-6 w-full"
                    size="lg"
                    onClick={handleCheckout}
                    isLoading={checkoutMutation.isPending}
                  >
                    <CreditCard className="mr-2 h-5 w-5" />
                    {isAuthenticated ? 'Proceed to Payment' : 'Sign in to Checkout'}
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>

                  {/* Security Badge */}
                  <div className="mt-4 flex items-center justify-center gap-2 text-sm text-gray-500">
                    <ShieldCheck className="h-4 w-4 text-green-500" />
                    <span>Secure checkout with 256-bit encryption</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
