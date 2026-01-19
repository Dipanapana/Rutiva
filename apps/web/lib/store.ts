import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  grade?: number;
}

interface CartItem {
  id: string;
  product_id?: string;
  bundle_id?: string;
  product?: {
    id: string;
    sku: string;
    title: string;
    price_zar: number;
    thumbnail_url?: string;
  };
  bundle?: {
    id: string;
    sku: string;
    title: string;
    price_zar: number;
    thumbnail_url?: string;
  };
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
}

interface CartState {
  items: CartItem[];
  totalZar: number;
  setCart: (items: CartItem[], totalZar: number) => void;
  clearCart: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);

export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],
      totalZar: 0,
      setCart: (items, totalZar) => set({ items, totalZar }),
      clearCart: () => set({ items: [], totalZar: 0 }),
    }),
    {
      name: 'cart-storage',
    }
  )
);
