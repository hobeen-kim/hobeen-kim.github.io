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
import { nodes as rawNodes, edges as rawEdges } from '../data/knowledge-graph.js'

const router = useRouter()
const container = ref(null)
const svgEl = ref(null)

let simulation = null
let resizeObserver = null

// Compute depth and branch color for each node
function computeNodeColors(nodes, edges) {
  const adj = {}
  nodes.forEach(n => { adj[n.id] = [] })
  edges.forEach(e => {
    adj[e.source]?.push(e.target)
  })

  const depthMap = {}
  const branchHueMap = {}

  // BFS from root
  const root = nodes.find(n => n.id === 'study-root')
  if (!root) return { depthMap, colorMap: {} }

  const queue = [{ id: root.id, depth: 0, baseHue: 0, parentHue: 0 }]
  depthMap[root.id] = 0
  branchHueMap[root.id] = 0

  // Hue assignments for depth-1 branches from root
  // 스마트농업 = green(140)
  // Future roots can get other hues (blue=220, purple=280, etc.)
  const branchHues = {
    'smart-agriculture': 140,  // 녹색 계열
    'software': 220,           // 파랑 계열
  }

  const visited = new Set([root.id])

  while (queue.length > 0) {
    const { id, depth, baseHue } = queue.shift()
    const children = adj[id] || []

    children.forEach((childId, idx) => {
      if (visited.has(childId)) return
      visited.add(childId)

      const childDepth = depth + 1
      depthMap[childId] = childDepth

      let childHue
      if (branchHues[childId] !== undefined) {
        // Explicit branch hue assignment
        childHue = branchHues[childId]
      } else if (childDepth === 2) {
        // Depth 2: spread children around parent hue
        const spread = 25
        const offset = (idx - (children.length - 1) / 2) * spread
        childHue = baseHue + offset
      } else {
        // Deeper: smaller variation from parent
        const spread = 15
        const offset = (idx - (children.length - 1) / 2) * spread
        childHue = baseHue + offset
      }

      branchHueMap[childId] = childHue
      queue.push({ id: childId, depth: childDepth, baseHue: childHue })
    })
  }

  // Generate HSL colors
  const colorMap = {}
  nodes.forEach(n => {
    const depth = depthMap[n.id] ?? 0
    const hue = branchHueMap[n.id] ?? 0

    if (n.id === 'study-root') {
      // Root: warm neutral
      colorMap[n.id] = { fill: '#6B7280', stroke: '#4B5563' }
    } else {
      // Saturation decreases, lightness increases with depth
      const saturation = Math.max(35, 65 - depth * 8)
      const lightness = Math.min(65, 42 + depth * 6)
      const fill = `hsl(${Math.round(hue)}, ${saturation}%, ${lightness}%)`
      const strokeL = Math.max(25, lightness - 12)
      const stroke = `hsl(${Math.round(hue)}, ${saturation + 5}%, ${strokeL}%)`
      colorMap[n.id] = { fill, stroke }
    }
  })

  return { depthMap, colorMap }
}

function initGraph() {
  const nodes = JSON.parse(JSON.stringify(rawNodes))
  const edges = JSON.parse(JSON.stringify(rawEdges))

  const { colorMap } = computeNodeColors(rawNodes, rawEdges)

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
    .attr('stroke-opacity', 0.3)
    .attr('stroke-width', 1.5)

  // Node layer
  const nodeGroup = svg.append('g').attr('class', 'nodes')
  const nodeEls = nodeGroup
    .selectAll('g')
    .data(nodes)
    .enter()
    .append('g')
    .attr('class', d => `node node-${d.id}`)
    .style('cursor', d => (d.status === 'active' && d.link) ? 'pointer' : 'default')

  // Circle with fill + stroke
  nodeEls.append('circle')
    .attr('r', d => d.size)
    .attr('fill', d => {
      if (d.status === 'planned') return 'transparent'
      return colorMap[d.id]?.fill || '#6B7280'
    })
    .attr('stroke', d => colorMap[d.id]?.stroke || '#4B5563')
    .attr('stroke-width', 2.5)
    .attr('stroke-dasharray', d => d.status === 'planned' ? '5,3' : null)
    .attr('opacity', 0.9)

  // Label inside circle
  nodeEls.each(function (d) {
    const g = select(this)
    const lines = d.label.split('\n')
    const fontSize = Math.min(13, Math.max(10, d.size * 0.35))

    if (lines.length === 1) {
      g.append('text')
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')
        .attr('dy', 0)
        .attr('font-size', fontSize + 'px')
        .attr('font-weight', '600')
        .attr('class', 'node-label')
        .text(d.label)
    } else {
      const totalHeight = lines.length * (fontSize + 2)
      lines.forEach((line, i) => {
        g.append('text')
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'central')
          .attr('dy', -totalHeight / 2 + (fontSize + 2) * i + (fontSize + 2) / 2)
          .attr('font-size', fontSize + 'px')
          .attr('font-weight', '600')
          .attr('class', 'node-label')
          .text(line)
      })
    }
  })

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
        return (srcId === d.id || tgtId === d.id) ? 0.8 : 0.05
      })
    })
    .on('mouseleave', function () {
      nodeEls.transition().duration(150).style('opacity', 1)
      linkEls.transition().duration(150).style('opacity', 0.3)
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
    .force('link', forceLink(edges).id(d => d.id).distance(100))
    .force('charge', forceManyBody().strength(-350))
    .force('center', forceCenter(width / 2, height / 2))
    .force('collide', forceCollide().radius(d => d.size + 15))
    .on('tick', () => {
      // Clamp nodes within bounds
      nodes.forEach(d => {
        const r = d.size + 3
        d.x = Math.max(r, Math.min(width - r, d.x))
        d.y = Math.max(r, Math.min(height - r, d.y))
      })

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
  fill: #fff;
  pointer-events: none;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}
</style>
