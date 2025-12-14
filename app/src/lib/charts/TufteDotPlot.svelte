<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import * as echarts from 'echarts';
	import type { EChartsOption } from 'echarts';
	
	interface DataPoint {
		name: string;
		value: number;
		category?: string;
	}
	
	interface Props {
		data: DataPoint[];
		xLabel?: string;
		yLabel?: string;
		height?: string;
		showZeroLine?: boolean;
	}
	
	let { 
		data, 
		xLabel = '', 
		yLabel = '', 
		height = '300px',
		showZeroLine = true 
	}: Props = $props();
	
	let chartContainer: HTMLDivElement;
	let chart: echarts.ECharts | null = null;
	
	// Tufte-compliant color palette
	const POSITIVE_COLOR = '#10b981';
	const NEGATIVE_COLOR = '#f43f5e';
	const NEUTRAL_COLOR = '#94a3b8';
	const GRID_COLOR = '#f1f5f9';
	const TEXT_COLOR = '#0f172a';
	
	function getColor(value: number): string {
		if (value > 0) return POSITIVE_COLOR;
		if (value < 0) return NEGATIVE_COLOR;
		return NEUTRAL_COLOR;
	}
	
	function buildOptions(): EChartsOption {
		// Sort by value for ranking view
		const sortedData = [...data].sort((a, b) => b.value - a.value);
		
		return {
			grid: {
				left: '3%',
				right: '4%',
				bottom: '3%',
				top: '8%',
				containLabel: true
			},
			xAxis: {
				type: 'category',
				data: sortedData.map(d => d.name),
				axisLine: { show: false },
				axisTick: { show: false },
				axisLabel: {
					color: TEXT_COLOR,
					fontSize: 11,
					fontFamily: 'Inter, sans-serif',
					rotate: sortedData.length > 8 ? 45 : 0
				},
				name: xLabel,
				nameLocation: 'center',
				nameGap: 35,
				nameTextStyle: {
					color: NEUTRAL_COLOR,
					fontSize: 12,
					fontFamily: 'Inter, sans-serif'
				}
			},
			yAxis: {
				type: 'value',
				axisLine: { show: false },
				axisTick: { show: false },
				splitLine: {
					show: true,
					lineStyle: {
						color: GRID_COLOR,
						type: 'solid'
					}
				},
				axisLabel: {
					color: TEXT_COLOR,
					fontSize: 11,
					fontFamily: 'Inter, sans-serif',
					formatter: (value: number) => value.toFixed(2)
				},
				name: yLabel,
				nameLocation: 'middle',
				nameGap: 50,
				nameTextStyle: {
					color: NEUTRAL_COLOR,
					fontSize: 12,
					fontFamily: 'Inter, sans-serif'
				}
			},
			series: [
				{
					type: 'scatter',
					symbolSize: 12,
					data: sortedData.map(d => ({
						value: d.value,
						itemStyle: {
							color: getColor(d.value),
							borderColor: '#fff',
							borderWidth: 1
						}
					})),
					emphasis: {
						itemStyle: {
							shadowBlur: 10,
							shadowColor: 'rgba(0, 0, 0, 0.2)'
						}
					}
				}
			],
			tooltip: {
				trigger: 'item',
				backgroundColor: '#fff',
				borderColor: '#e2e8f0',
				borderWidth: 1,
				textStyle: {
					color: TEXT_COLOR,
					fontFamily: 'Inter, sans-serif'
				},
				formatter: (params: any) => {
					const d = sortedData[params.dataIndex];
					const sign = d.value >= 0 ? '+' : '';
					const colorClass = d.value >= 0 ? '#10b981' : '#f43f5e';
					return `<strong>${d.name}</strong><br/><span style="color:${colorClass}">${sign}${d.value.toFixed(3)}</span>`;
				}
			}
		};
	}
	
	$effect(() => {
		if (chart && data) {
			chart.setOption(buildOptions());
		}
	});
	
	onMount(() => {
		chart = echarts.init(chartContainer);
		chart.setOption(buildOptions());
		
		const handleResize = () => chart?.resize();
		window.addEventListener('resize', handleResize);
		
		return () => {
			window.removeEventListener('resize', handleResize);
		};
	});
	
	onDestroy(() => {
		chart?.dispose();
	});
</script>

<div class="chart-wrapper" style="height: {height}">
	<div bind:this={chartContainer} class="chart-container"></div>
</div>

<style>
	.chart-wrapper {
		width: 100%;
		position: relative;
	}
	
	.chart-container {
		width: 100%;
		height: 100%;
	}
</style>
