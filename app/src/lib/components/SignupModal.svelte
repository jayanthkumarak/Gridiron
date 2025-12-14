<script lang="ts">
	import { SignIn } from 'svelte-clerk';
	
	interface Props {
		onclose?: () => void;
	}
	
	let { onclose }: Props = $props();

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
			<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M18 6L6 18M6 6l12 12"/>
			</svg>
		</button>

		<div class="clerk-wrapper">
			<SignIn 
				appearance={{
					elements: {
						rootBox: 'clerk-root',
						card: 'clerk-card'
					}
				}}
			/>
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
		top: var(--space-3);
		right: var(--space-3);
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
		z-index: 10;
	}

	.close-btn:hover {
		background: var(--color-bg-subtle);
		color: var(--color-text);
	}

	.clerk-wrapper {
		padding: var(--space-4);
	}

	:global(.clerk-root) {
		width: 100%;
	}

	:global(.clerk-card) {
		box-shadow: none !important;
	}
</style>
