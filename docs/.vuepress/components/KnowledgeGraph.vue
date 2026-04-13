<template>
  <div class="knowledge-graph-container">
    <h1 class="graph-title">공부하기</h1>
    <div ref="container" class="graph-svg-wrapper">
      <svg ref="svgEl"></svg>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide } from 'd3-force'
import { select } from 'd3-selection'
import { drag } from 'd3-drag'
import 'd3-transition'
import { nodes as rawNodes, edges as rawEdges, CATEGORY_COLORS } from '../data/knowledge-graph.js'

const router = useRouter()
const container = ref(null)
const svgEl = ref(null)

let simulation = null
let resizeObserver = null

function initGraph() {
  const nodes = JSON.parse(JSON.stringify(rawNodes))
  const edges = JSON.parse(JSON.stringify(rawEdges))

  const width = container.value.clientWidth
  const height = container.value.clientHeight

  const svg = select(svgEl.value)
    .attr('width', width)
    .attr('height', height)

  svg.selectAll('*').remove()

  // Edge layer
  const linkGroup = svg.append('g').attr('class', 'links')
  const linkEls = linkGroup
    .selectAll('line')
    .data(edges)
    .enter()
    .append('line')
    .attr('stroke', '#999')
    .attr('stroke-opacity', 0.4)
    .attr('stroke-width', 1.5)

  // Node layer
  const nodeGroup = svg.append('g').attr('class', 'nodes')
  const nodeEls = nodeGroup
    .selectAll('g')
    .data(nodes)
    .enter()
    .append('g')
    .attr('class', d => `node node-${d.id}`)
    .style('cursor', d => d.status === 'active' ? 'pointer' : 'default')

  // Circle
  nodeEls.append('circle')
    .attr('r', d => d.size)
    .attr('fill', d => d.status === 'active' ? CATEGORY_COLORS[d.category] : 'transparent')
    .attr('stroke', d => CATEGORY_COLORS[d.category])
    .attr('stroke-width', d => d.status === 'planned' ? 2 : 0)
    .attr('stroke-dasharray', d => d.status === 'planned' ? '4,4' : null)
    .attr('opacity', d => d.status === 'active' ? 0.85 : 1)

  // Label
  nodeEls.append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', d => d.size + 14)
    .attr('font-size', d => Math.min(16, Math.max(12, d.size * 0.45)) + 'px')
    .attr('class', 'node-label')
    .text(d => d.label)

  // Hover interaction
  nodeEls
    .on('mouseenter', function (event, d) {
      const connectedIds = new Set([d.id])
      edges.forEach(e => {
        const srcId = typeof e.source === 'object' ? e.source.id : e.source
        const tgtId = typeof e.target === 'object' ? e.target.id : e.target
        if (srcId === d.id) connectedIds.add(tgtId)
        if (tgtId === d.id) connectedIds.add(srcId)
      })

      nodeEls.transition().duration(150).style('opacity', n => connectedIds.has(n.id) ? 1 : 0.15)
      linkEls.transition().duration(150).style('opacity', e => {
        const srcId = typeof e.source === 'object' ? e.source.id : e.source
        const tgtId = typeof e.target === 'object' ? e.target.id : e.target
        return (srcId === d.id || tgtId === d.id) ? 1 : 0.05
      })
    })
    .on('mouseleave', function () {
      nodeEls.transition().duration(150).style('opacity', 1)
      linkEls.transition().duration(150).style('opacity', 0.4)
    })

  // Click interaction
  nodeEls.on('click', function (event, d) {
    if (d.status === 'active' && d.link) {
      router.push(d.link)
    }
  })

  // Drag interaction
  const dragHandler = drag()
    .on('start', function (event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    })
    .on('drag', function (event, d) {
      d.fx = event.x
      d.fy = event.y
    })
    .on('end', function (event, d) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    })

  nodeEls.call(dragHandler)

  // Force simulation
  simulation = forceSimulation(nodes)
    .force('link', forceLink(edges).id(d => d.id).distance(120))
    .force('charge', forceManyBody().strength(-300))
    .force('center', forceCenter(width / 2, height / 2))
    .force('collide', forceCollide().radius(d => d.size + 20))
    .on('tick', () => {
      linkEls
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)

      nodeEls.attr('transform', d => `translate(${d.x},${d.y})`)
    })
}

onMounted(() => {
  initGraph()

  resizeObserver = new ResizeObserver(() => {
    if (!container.value || !svgEl.value || !simulation) return
    const width = container.value.clientWidth
    const height = container.value.clientHeight

    select(svgEl.value)
      .attr('width', width)
      .attr('height', height)

    simulation
      .force('center', forceCenter(width / 2, height / 2))
      .alpha(0.3)
      .restart()
  })

  resizeObserver.observe(container.value)
})

onUnmounted(() => {
  if (simulation) simulation.stop()
  if (resizeObserver) resizeObserver.disconnect()
})
</script>

<style scoped>
.knowledge-graph-container {
  width: 100%;
  position: relative;
}

.graph-title {
  font-size: 1.875rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  margin-top: 1rem;
}

.graph-svg-wrapper {
  width: 100%;
  min-height: 600px;
  position: relative;
}

.graph-svg-wrapper svg {
  width: 100%;
  height: 100%;
  min-height: 600px;
  display: block;
}

.graph-svg-wrapper :deep(.node-label) {
  fill: var(--vp-c-text-1);
  pointer-events: none;
}
</style>
