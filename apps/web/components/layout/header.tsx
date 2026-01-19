'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { Menu, X, ShoppingCart, User, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuthStore, useCartStore } from '@/lib/store';
import { cn } from '@/lib/utils';

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const { isAuthenticated, user } = useAuthStore();
  const { items } = useCartStore();

  const navigation = [
    { name: 'Study Guides', href: '/shop/shop' },
    { name: 'My Library', href: '/library', authRequired: true },
    { name: 'How It Works', href: '/#how-it-works' },
    { name: 'Pricing', href: '/#pricing' },
    { name: 'Schools', href: '/schools' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-100 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-600">
            <BookOpen className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold text-gray-900">Rutiva</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex md:items-center md:space-x-8">
          {navigation.map((item) => {
            // Skip auth-required items if not authenticated
            if (item.authRequired && !isAuthenticated) return null;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'text-sm font-medium transition-colors',
                  pathname === item.href
                    ? 'text-primary-600'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                {item.name}
              </Link>
            );
          })}
        </div>

        {/* Desktop Actions */}
        <div className="hidden md:flex md:items-center md:space-x-4">
          <Link href="/cart" className="relative p-2 text-gray-600 hover:text-gray-900">
            <ShoppingCart className="h-5 w-5" />
            {items.length > 0 && (
              <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary-600 text-xs font-medium text-white">
                {items.length}
              </span>
            )}
          </Link>

          {isAuthenticated ? (
            <Link href="/library">
              <Button variant="outline" size="sm">
                <User className="mr-2 h-4 w-4" />
                {user?.first_name}
              </Button>
            </Link>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm">Get Started</Button>
              </Link>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          type="button"
          className="md:hidden p-2 text-gray-600"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Menu className="h-6 w-6" />
          )}
        </button>
      </nav>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-100">
          <div className="space-y-1 px-4 py-4">
            {navigation.map((item) => {
              // Skip auth-required items if not authenticated
              if (item.authRequired && !isAuthenticated) return null;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'block rounded-lg px-3 py-2 text-base font-medium',
                    pathname === item.href
                      ? 'bg-primary-50 text-primary-600'
                      : 'text-gray-600 hover:bg-gray-50'
                  )}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              );
            })}
            <div className="mt-4 flex flex-col space-y-2 pt-4 border-t border-gray-100">
              {isAuthenticated ? (
                <Link href="/library">
                  <Button variant="outline" className="w-full">
                    My Library
                  </Button>
                </Link>
              ) : (
                <>
                  <Link href="/login">
                    <Button variant="outline" className="w-full">
                      Sign In
                    </Button>
                  </Link>
                  <Link href="/register">
                    <Button className="w-full">Get Started</Button>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
