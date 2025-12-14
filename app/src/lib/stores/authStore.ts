// Auth Store - Query tracking and signup gate logic
import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';

const STORAGE_KEY = 'gridiron_auth';
const FREE_QUERY_LIMIT = 3;
const GUEST_BONUS_QUERIES = 1;

interface AuthState {
    isAuthenticated: boolean;
    user: User | null;
    queryCount: number;
    guestBonusUsed: boolean;
    showSignupModal: boolean;
}

interface User {
    id: string;
    email: string;
    name: string;
    avatarUrl?: string;
    provider: 'google' | 'twitter' | 'email';
}

function createAuthStore() {
    const defaultState: AuthState = {
        isAuthenticated: false,
        user: null,
        queryCount: 0,
        guestBonusUsed: false,
        showSignupModal: false
    };

    // Load from localStorage
    const stored = browser ? localStorage.getItem(STORAGE_KEY) : null;
    const initial: AuthState = stored ? { ...defaultState, ...JSON.parse(stored) } : defaultState;

    const { subscribe, set, update } = writable<AuthState>(initial);

    // Persist to localStorage on changes
    if (browser) {
        subscribe((state) => {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
                queryCount: state.queryCount,
                guestBonusUsed: state.guestBonusUsed,
                isAuthenticated: state.isAuthenticated,
                user: state.user
            }));
        });
    }

    return {
        subscribe,

        // Check if user can make a query
        canQuery(): boolean {
            const state = get({ subscribe });
            if (state.isAuthenticated) return true;

            const limit = state.guestBonusUsed
                ? FREE_QUERY_LIMIT + GUEST_BONUS_QUERIES
                : FREE_QUERY_LIMIT;

            return state.queryCount < limit;
        },

        // Get remaining free queries
        remainingQueries(): number {
            const state = get({ subscribe });
            if (state.isAuthenticated) return Infinity;

            const limit = state.guestBonusUsed
                ? FREE_QUERY_LIMIT + GUEST_BONUS_QUERIES
                : FREE_QUERY_LIMIT;

            return Math.max(0, limit - state.queryCount);
        },

        // Increment query count and check if gate should show
        recordQuery(): boolean {
            let shouldShowGate = false;

            update((state) => {
                if (state.isAuthenticated) return state;

                const newCount = state.queryCount + 1;
                const limit = state.guestBonusUsed
                    ? FREE_QUERY_LIMIT + GUEST_BONUS_QUERIES
                    : FREE_QUERY_LIMIT;

                if (newCount >= limit) {
                    shouldShowGate = true;
                }

                return { ...state, queryCount: newCount };
            });

            return shouldShowGate;
        },

        // Show signup modal
        showModal() {
            update((state) => ({ ...state, showSignupModal: true }));
        },

        // Hide signup modal
        hideModal() {
            update((state) => ({ ...state, showSignupModal: false }));
        },

        // Continue as guest (grants 1 bonus query)
        continueAsGuest() {
            update((state) => ({
                ...state,
                guestBonusUsed: true,
                showSignupModal: false
            }));
        },

        // Login user
        login(user: User) {
            update((state) => ({
                ...state,
                isAuthenticated: true,
                user,
                showSignupModal: false
            }));
        },

        // Logout user
        logout() {
            update((state) => ({
                ...state,
                isAuthenticated: false,
                user: null
            }));
        },

        // Reset for testing
        reset() {
            set(defaultState);
            if (browser) {
                localStorage.removeItem(STORAGE_KEY);
            }
        }
    };
}

export const authStore = createAuthStore();
export type { User, AuthState };
