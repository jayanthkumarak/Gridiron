<script lang="ts">
	import Icon from '@iconify/svelte';
	
	interface Props {
		value?: string;
		placeholder?: string;
		disabled?: boolean;
		onsubmit?: (query: string) => void;
	}
	
	let { 
		value = $bindable(''), 
		placeholder = 'Ask anything about NFL stats...',
		disabled = false,
		onsubmit 
	}: Props = $props();

	let isFocused = $state(false);
	
	function handleSubmit() {
		if (value.trim() && !disabled) {
			onsubmit?.(value.trim());
		}
	}
	
	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSubmit();
		}
	}
</script>

<div class="chat-input-container">
	<div class="input-wrapper" class:disabled class:focused={isFocused}>
		<div class="input-icon">
			<Icon icon="lucide:search" width="20" height="20" />
		</div>
		<input
			type="text"
			bind:value
			{placeholder}
			{disabled}
			onkeydown={handleKeydown}
			onfocus={() => isFocused = true}
			onblur={() => isFocused = false}
			class="chat-input"
		/>
		<button 
			class="send-button" 
			class:active={value.trim().length > 0}
			onclick={handleSubmit}
			disabled={disabled || !value.trim()}
			aria-label="Send message"
		>
			{#if disabled}
				<div class="spinner"></div>
			{:else}
				<Icon icon="lucide:arrow-up" width="18" height="18" />
			{/if}
		</button>
	</div>
</div>

<style>
	.chat-input-container {
		max-width: 48rem;
		margin: 0 auto;
		animation: fadeInUp var(--transition-slow) ease-out;
	}
	
	.input-wrapper {
		display: flex;
		align-items: center;
		gap: var(--space-3);
		background: var(--color-surface);
		border: 1.5px solid var(--color-border);
		border-radius: var(--radius-2xl);
		padding: var(--space-2) var(--space-3) var(--space-2) var(--space-4);
		box-shadow: var(--shadow-lg);
		transition: all var(--transition-base);
	}
	
	.input-wrapper.focused {
		border-color: var(--accent);
		box-shadow: var(--shadow-lg), 0 0 0 4px var(--accent-glow);
		transform: translateY(-1px);
	}
	
	.input-wrapper.disabled {
		opacity: 0.6;
		pointer-events: none;
	}
	
	.input-icon {
		color: var(--color-text-tertiary);
		display: flex;
		align-items: center;
		transition: color var(--transition-fast);
	}

	.input-wrapper.focused .input-icon {
		color: var(--accent);
	}
	
	.chat-input {
		flex: 1;
		border: none;
		background: transparent;
		font-size: var(--text-base);
		color: var(--color-text);
		outline: none;
		padding: var(--space-2) 0;
		min-width: 0;
	}
	
	.chat-input::placeholder {
		color: var(--color-text-tertiary);
	}
	
	.send-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2.5rem;
		height: 2.5rem;
		border: none;
		border-radius: var(--radius-full);
		background: var(--color-border);
		color: var(--color-text-tertiary);
		cursor: pointer;
		transition: all var(--transition-base);
		flex-shrink: 0;
	}
	
	.send-button.active {
		background: var(--accent);
		color: white;
	}
	
	.send-button.active:hover:not(:disabled) {
		background: var(--accent-soft);
		transform: scale(1.08);
		box-shadow: var(--shadow-glow);
	}

	.send-button.active:active:not(:disabled) {
		transform: scale(0.95);
	}
	
	.send-button:disabled {
		cursor: not-allowed;
	}

	.spinner {
		width: 18px;
		height: 18px;
		border: 2px solid transparent;
		border-top-color: currentColor;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes fadeInUp {
		from { opacity: 0; transform: translateY(10px); }
		to { opacity: 1; transform: translateY(0); }
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
