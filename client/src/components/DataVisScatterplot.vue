<template>
  <svg id="vis">
  </svg>
</template>

<script>
import * as d3 from "d3";

export default {
  data() {
    return {
      svg: null
    };
  },
  methods: {
    setupSVG() {
      this.svg = d3.select('#vis');
      this.svg.attr('width', 600).attr('height', 600).append('g').classed('scatterplot', true);
      this.setupVis();
    },
    setupVis() {
      let g = this.svg.select('.scatterplot');
      g.append('circle').attr('cx', 250).attr('cy', 250).attr('r', 20);
      this.addAxes(g);
    },
    addAxes(g) {
      let xAxis = g.append('g').attr('id', 'x-axis')
          .attr('transform', 'rotate(-90, 0, 0)')
      .attr('transform', 'translate(100,35)');
      xAxis.append('text')
        .attr('transform', 'translate(100,35)')
        .attr('transform', 'rotate(-90, 0, 0)').text('yAxis');
      let yAxis = g.append('g').attr('id', 'y-axis');
      yAxis.append('text').text('yAxis');

    },
    selectPolygon() {
    },
    resetLeafletMapLayers() {
    },
    resetMapView() {
    }
  },
  mounted() {
    this.setupSVG();
  }
};
</script>

<style scoped>

</style>
