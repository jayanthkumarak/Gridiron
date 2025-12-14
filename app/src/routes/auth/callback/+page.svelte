<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/authStore';
	import Icon from '@iconify/svelte';

	let status = $state<'loading' | 'success' | 'error'>('loading');
	let errorMessage = $state('');

	onMount(() => {
		const params = $page.url.searchParams;
		
		// Check for error
		const error = params.get('error');
		if (error) {
			status = 'error';
			errorMessage = error.replace(/_/g, ' ');
			return;
		}
		
		// Get tokens from URL
		const accessToken = params.get('access_token');
		const refreshToken = params.get('refresh_token');
		
		if (accessToken && refreshToken) {
			// Store tokens
			localStorage.setItem('gridiron_access_token', accessToken);
			localStorage.setItem('gridiron_refresh_token', refreshToken);
			
			// Decode user from token (simple JWT decode, no verification)
			try {
				const payload = JSON.parse(atob(accessToken.split('.')[1]));
				authStore.login({
					id: payload.sub,
					email: payload.email || '',
					name: payload.name || payload.email?.split('@')[0] || 'User',
					provider: 'oauth' as any
				});
				
				status = 'success';
				
				// Redirect to home after short delay
				setTimeout(() => goto('/'), 1500);
			} catch (e) {
				status = 'error';
				errorMessage = 'Failed to process authentication';
			}
		} else {
			status = 'error';
			errorMessage = 'Missing authentication tokens';
		}
	});
</script>

<div class="callback-page">
	<div class="callback-card">
		{#if status === 'loading'}
			<div class="loading">
				<div class="spinner"></div>
				<p>Completing sign in...</p>
			</div>
		{:else if status === 'success'}
			<div class="success">
				<div class="success-icon">
					<Icon icon="lucide:check" width="32" height="32" />
				</div>
				<h2>Welcome to Gridiron!</h2>
				<p>Redirecting you to the app...</p>
			</div>
		{:else}
			<div class="error">
				<div class="error-icon">
					<Icon icon="lucide:x" width="32" height="32" />
				</div>
				<h2>Authentication Failed</h2>
				<p>{errorMessage}</p>
				<a href="/" class="btn-home">Return Home</a>
			</div>
		{/if}
	</div>
</div>

<style>
	.callback-page {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--space-6);
		background: var(--color-bg);
	}

	.callback-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-2xl);
		padding: var(--space-10);
		text-align: center;
		max-width: 24rem;
		box-shadow: var(--shadow-lg);
	}

	.loading, .success, .error {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--space-4);
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 3px solid var(--color-border);
		border-top-color: var(--accent);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	.success-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 4rem;
		height: 4rem;
		background: var(--color-positive);
		color: white;
		border-radius: 50%;
		animation: scaleIn 0.3s ease-out;
	}

	.error-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 4rem;
		height: 4rem;
		background: var(--color-negative);
		color: white;
		border-radius: 50%;
	}

	@keyframes scaleIn {
		from { transform: scale(0); }
		to { transform: scale(1); }
	}

	h2 {
		font-size: var(--text-xl);
		font-weight: 600;
		margin: 0;
	}

	p {
		color: var(--color-text-secondary);
		margin: 0;
	}

	.btn-home {
		display: inline-block;
		margin-top: var(--space-4);
		padding: var(--space-3) var(--space-6);
		background: var(--accent);
		color: white;
		text-decoration: none;
		border-radius: var(--radius-lg);
		font-weight: 500;
		transition: background var(--transition-fast);
	}

	.btn-home:hover {
		background: var(--accent-soft);
	}
</style>
