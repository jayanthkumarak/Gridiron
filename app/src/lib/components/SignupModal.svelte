<script lang="ts">
	import Icon from '@iconify/svelte';
	import { authStore } from '$lib/stores/authStore';
	
	interface Props {
		onclose?: () => void;
	}
	
	let { onclose }: Props = $props();
	let email = $state('');
	let isSubmitting = $state(false);

	const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

	async function handleGoogleLogin() {
		try {
			const res = await fetch(`${API_URL}/auth/google`);
			const data = await res.json();
			if (data.url) {
				window.location.href = data.url;
			}
		} catch (error) {
			console.error('Google login error:', error);
		}
	}

	async function handleTwitterLogin() {
		try {
			const res = await fetch(`${API_URL}/auth/twitter`);
			const data = await res.json();
			if (data.url) {
				window.location.href = data.url;
			}
		} catch (error) {
			console.error('Twitter login error:', error);
		}
	}

	async function handleEmailSubmit() {
		if (!email.trim()) return;
		
		isSubmitting = true;
		// For email signup, we'll just log them in locally for now
		// A real implementation would send a magic link
		await new Promise(r => setTimeout(r, 800));
		
		authStore.login({
			id: `email-${Date.now()}`,
			email: email.trim(),
			name: email.split('@')[0],
			provider: 'email'
		});
		
		isSubmitting = false;
	}

	function handleContinueAsGuest() {
		authStore.continueAsGuest();
		onclose?.();
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			onclose?.();
		}
	}
</script>

<div 
	class="modal-backdrop" 
	onclick={handleBackdropClick}
	onkeydown={(e) => e.key === 'Escape' && onclose?.()}
	role="dialog"
	aria-modal="true"
	tabindex="-1"
>
	<div class="modal-container">
		<button class="close-btn" onclick={onclose} aria-label="Close">
			<Icon icon="lucide:x" width="20" height="20" />
		</button>

		<div class="modal-header">
			<div class="modal-icon">
				<Icon icon="lucide:zap" width="24" height="24" />
			</div>
			<h2>Unlock Unlimited Analysis</h2>
			<p>Create a free account to save your queries and get unlimited access.</p>
		</div>

		<div class="modal-body">
			<div class="social-buttons">
				<button class="social-btn google" onclick={handleGoogleLogin}>
					<Icon icon="logos:google-icon" width="20" height="20" />
					<span>Continue with Google</span>
				</button>
				
				<button class="social-btn twitter" onclick={handleTwitterLogin}>
					<Icon icon="simple-icons:x" width="18" height="18" />
					<span>Continue with X</span>
				</button>
			</div>

			<div class="divider">
				<span>or</span>
			</div>

			<form class="email-form" onsubmit={(e) => { e.preventDefault(); handleEmailSubmit(); }}>
				<input
					type="email"
					bind:value={email}
					placeholder="Enter your email"
					class="email-input"
					required
				/>
				<button type="submit" class="email-btn" disabled={isSubmitting || !email.trim()}>
					{#if isSubmitting}
						<div class="spinner"></div>
					{:else}
						<span>Get Started</span>
						<Icon icon="lucide:arrow-right" width="16" height="16" />
					{/if}
				</button>
			</form>

			<p class="privacy-note">
				No spam, ever. We respect your privacy.
			</p>
		</div>

		<div class="modal-footer">
			<button class="guest-btn" onclick={handleContinueAsGuest}>
				Continue as guest (1 more free query)
			</button>
		</div>
	</div>
</div>

<style>
	.modal-backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.4);
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--space-4);
		z-index: 100;
		animation: fadeIn 0.2s ease-out;
	}

	.modal-container {
		position: relative;
		width: 100%;
		max-width: 24rem;
		background: var(--color-surface);
		border-radius: var(--radius-2xl);
		box-shadow: var(--shadow-xl);
		overflow: hidden;
		animation: modalEnter 0.3s ease-out;
	}

	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}

	@keyframes modalEnter {
		from {
			opacity: 0;
			transform: scale(0.95) translateY(10px);
		}
		to {
			opacity: 1;
			transform: scale(1) translateY(0);
		}
	}

	.close-btn {
		position: absolute;
		top: var(--space-4);
		right: var(--space-4);
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2rem;
		height: 2rem;
		background: transparent;
		border: none;
		border-radius: var(--radius-full);
		color: var(--color-text-tertiary);
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.close-btn:hover {
		background: var(--color-bg-subtle);
		color: var(--color-text);
	}

	.modal-header {
		text-align: center;
		padding: var(--space-8) var(--space-6) var(--space-4);
	}

	.modal-icon {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 3rem;
		height: 3rem;
		background: var(--accent-glow);
		color: var(--accent);
		border-radius: var(--radius-xl);
		margin-bottom: var(--space-4);
	}

	.modal-header h2 {
		font-size: var(--text-xl);
		font-weight: 600;
		margin-bottom: var(--space-2);
	}

	.modal-header p {
		color: var(--color-text-secondary);
		font-size: var(--text-sm);
		margin: 0 auto;
		max-width: 18rem;
	}

	.modal-body {
		padding: var(--space-4) var(--space-6);
	}

	.social-buttons {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
	}

	.social-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-3);
		width: 100%;
		padding: var(--space-3) var(--space-4);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		font-size: var(--text-sm);
		font-weight: 500;
		color: var(--color-text);
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.social-btn:hover {
		background: var(--color-bg-subtle);
		border-color: var(--color-text-tertiary);
		transform: translateY(-1px);
	}

	.social-btn.twitter {
		background: var(--black);
		color: white;
		border-color: var(--black);
	}

	.social-btn.twitter:hover {
		background: var(--gray-800);
	}

	.divider {
		display: flex;
		align-items: center;
		gap: var(--space-4);
		margin: var(--space-5) 0;
	}

	.divider::before,
	.divider::after {
		content: '';
		flex: 1;
		height: 1px;
		background: var(--color-border);
	}

	.divider span {
		font-size: var(--text-sm);
		color: var(--color-text-tertiary);
	}

	.email-form {
		display: flex;
		gap: var(--space-2);
	}

	.email-input {
		flex: 1;
		padding: var(--space-3) var(--space-4);
		font-size: var(--text-sm);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		color: var(--color-text);
		outline: none;
		transition: all var(--transition-fast);
	}

	.email-input:focus {
		border-color: var(--accent);
		box-shadow: 0 0 0 3px var(--accent-glow);
	}

	.email-btn {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		padding: var(--space-3) var(--space-4);
		background: var(--accent);
		color: white;
		border: none;
		border-radius: var(--radius-lg);
		font-size: var(--text-sm);
		font-weight: 500;
		cursor: pointer;
		transition: all var(--transition-fast);
	}

	.email-btn:hover:not(:disabled) {
		background: var(--accent-soft);
	}

	.email-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid transparent;
		border-top-color: currentColor;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	.privacy-note {
		text-align: center;
		font-size: var(--text-xs);
		color: var(--color-text-tertiary);
		margin-top: var(--space-4);
	}

	.modal-footer {
		padding: var(--space-4) var(--space-6) var(--space-6);
		border-top: 1px solid var(--color-border);
	}

	.guest-btn {
		width: 100%;
		padding: var(--space-3);
		background: transparent;
		border: none;
		font-size: var(--text-sm);
		color: var(--color-text-secondary);
		cursor: pointer;
		transition: color var(--transition-fast);
	}

	.guest-btn:hover {
		color: var(--color-text);
	}
</style>
