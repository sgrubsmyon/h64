<script setup>
import { gsap } from "gsap";
import { MotionPathPlugin } from "gsap/MotionPathPlugin";
import { onMounted } from "vue";

gsap.registerPlugin(MotionPathPlugin);

onMounted(() => {
  gsap.to(".current-power-load-arrow", {
    motionPath: {
      path: "#current-power-arrow-path-load",
      align: "#current-power-arrow-path-load",
      alignOrigin: [0.5, 0.5],
      autoRotate: 30,
    },
    transformOrigin: "50% 50%",
    duration: 10,
    repeat: -1,
    stagger: 0.6,
    ease: "none",
  });

  gsap.to(".current-power-pv-arrow", {
    motionPath: {
      path: "#current-power-arrow-path-pv",
      align: "#current-power-arrow-path-pv",
      alignOrigin: [0.5, 0.5],
      autoRotate: 0,
    },
    transformOrigin: "50% 50%",
    duration: 10,
    repeat: -1,
    stagger: 0.6,
    ease: "none",
  });

  // gsap.to(".current-power-battery-charge-arrow", {
  //   motionPath: {
  //     path: "#current-power-arrow-path-battery-charge",
  //     align: "#current-power-arrow-path-battery-charge",
  //     alignOrigin: [0.5, 0.5],
  //     autoRotate: 30,
  //   },
  //   transformOrigin: "50% 50%",
  //   duration: 10,
  //   repeat: -1,
  //   stagger: 0.6,
  //   ease: "none",
  // });

  gsap.to(".current-power-battery-discharge-arrow", {
    motionPath: {
      path: "#current-power-arrow-path-battery-discharge",
      align: "#current-power-arrow-path-battery-discharge",
      alignOrigin: [0.5, 0.5],
      autoRotate: 0,
    },
    transformOrigin: "50% 50%",
    duration: 10,
    repeat: -1,
    stagger: 0.6,
    ease: "none",
  });

  // gsap.to(".current-power-grid-sell-arrow", {
  //   motionPath: {
  //     path: "#current-power-arrow-path-grid-sell",
  //     align: "#current-power-arrow-path-grid-sell",
  //     alignOrigin: [0.5, 0.5],
  //     autoRotate: 210,
  //   },
  //   transformOrigin: "50% 50%",
  //   duration: 10,
  //   repeat: -1,
  //   stagger: 0.6,
  //   ease: "none",
  // });

  gsap.to(".current-power-grid-buy-arrow", {
    motionPath: {
      path: "#current-power-arrow-path-grid-buy",
      align: "#current-power-arrow-path-grid-buy",
      alignOrigin: [0.5, 0.5],
      autoRotate: 180,
    },
    transformOrigin: "50% 50%",
    duration: 10,
    repeat: -1,
    stagger: 0.6,
    ease: "none",
  });
});
</script>

<template>
  <svg width="100%" height="100%" version="1.1" viewBox="0 0 210 190" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink">
    <defs>
      <linearGradient id="linearGradientPipePV" gradientTransform="rotate(0)">
        <stop offset="0%" stop-color="#666666" />
        <stop offset="100%" stop-color="#eeeeee" />
      </linearGradient>
      <linearGradient id="linearGradientPipeBattery" gradientTransform="rotate(0)">
        <stop offset="0%" stop-color="#666666" />
        <stop offset="100%" stop-color="#eeeeee" />
      </linearGradient>
      <linearGradient id="linearGradientPipeGrid" gradientTransform="rotate(0)">
        <stop offset="0%" stop-color="#eeeeee" />
        <stop offset="100%" stop-color="#666666" />
      </linearGradient>
      <linearGradient id="linearGradientPipeLoad" gradientTransform="rotate(0)">
        <stop offset="0%" stop-color="#eeeeee" />
        <stop offset="100%" stop-color="#666666" />
      </linearGradient>
    </defs>
    <path id="current-power-battery-discharge-arrow-one" class="current-power-battery-discharge-arrow"
      d="m46.054 152.3v4l3.4637-2z" fill="#7ffefe" />
    <path id="current-power-battery-discharge-arrow-two" class="current-power-battery-discharge-arrow"
      d="m51.054 152.3v4l3.4637-2z" fill="#7ffefe" />
    <path id="current-power-battery-discharge-arrow-three" class="current-power-battery-discharge-arrow"
      d="m56.054 152.3v4l3.4637-2z" fill="#7ffefe" />
    <path id="current-power-battery-charge-arrow-one" class="current-power-battery-charge-arrow"
      d="m93.51 105.97h-4l2 3.4637z" fill="#7ffefe" />
    <path id="current-power-battery-charge-arrow-two" class="current-power-battery-charge-arrow"
      d="m93.51 110.97h-4l2 3.4637z" fill="#7ffefe" />
    <path id="current-power-battery-charge-arrow-three" class="current-power-battery-charge-arrow"
      d="m93.51 115.97h-4l2 3.4637z" fill="#7ffefe" />
    <path id="current-power-load-arrow-one" class="current-power-load-arrow" d="m116.52 105.98h4l-2 3.4637z"
      fill="#7ffefe" />
    <path id="current-power-load-arrow-two" class="current-power-load-arrow" d="m116.52 110.98h4l-2 3.4637z"
      fill="#7ffefe" />
    <path id="current-power-load-arrow-three" class="current-power-load-arrow" d="m116.52 115.98h4l-2 3.4637z"
      fill="#7ffefe" />
    <path id="current-power-grid-buy-arrow-one" class="current-power-grid-buy-arrow" d="m163.98 36.346v-4l-3.4637 2z"
      fill="#7ffefe" />
    <path id="current-power-grid-buy-arrow-two" class="current-power-grid-buy-arrow" d="m158.98 36.346v-4l-3.4637 2z"
      fill="#7ffefe" />
    <path id="current-power-grid-buy-arrow-three" class="current-power-grid-buy-arrow" d="m153.98 36.346v-4l-3.4637 2z"
      fill="#7ffefe" />
    <path id="current-power-grid-sell-arrow-one" class="current-power-grid-sell-arrow" d="m116.52 84.258h4l-2-3.4637z"
      fill="#7ffefe" />
    <path id="current-power-grid-sell-arrow-two" class="current-power-grid-sell-arrow" d="m116.52 79.258h4l-2-3.4637z"
      fill="#7ffefe" />
    <path id="current-power-grid-sell-arrow-three" class="current-power-grid-sell-arrow" d="m116.52 74.258h4l-2-3.4637z"
      fill="#7ffefe" />
    <path id="current-power-pv-arrow-one" class="current-power-pv-arrow" d="m46.069 36.35v-4l3.4637 2z" fill="#7ffefe" />
    <path id="current-power-pv-arrow-two" class="current-power-pv-arrow" d="m51.069 36.35v-4l3.4637 2z" fill="#7ffefe" />
    <path id="current-power-pv-arrow-three" class="current-power-pv-arrow" d="m56.069 36.35v-4l3.4637 2z"
      fill="#7ffefe" />
    <path id="current-power-arrow-path-grid-buy"
      d="m164.89 34.339h-34.975c-7.1263 0-9.416 4.1037-9.416 4.1037-1.4589 1.5825-1.9771 4.7445-1.9771 8.1595v38.495"
      fill="none" />
    <path id="current-power-arrow-path-grid-sell"
      d="m119.05 85.097v-38.495c0-3.415-0.011-6.577 1.4479-8.1595 0 0 2.2897-3.5745 9.416-3.5745h34.975" fill="none" />
    <path id="current-power-arrow-path-pv"
      d="m44.595 34.316h34.975c7.1263 0 9.416 4.1037 9.416 4.1037 1.4589 1.5825 1.9771 4.7445 1.9771 8.1595v38.495"
      fill="none" />
    <path id="current-power-arrow-path-battery-discharge"
      d="m45.048 154.4h34.975c7.1263 0 9.416-4.1037 9.416-4.1037 1.4589-1.5825 1.9771-4.7445 1.9771-8.1595v-38.495"
      fill="none" />
    <path id="current-power-arrow-path-battery-charge"
      d="m90.887 103.64v38.495c0 3.415 0.01097 6.577-1.4479 8.1595 0 0-2.2897 3.5745-9.416 3.5745h-34.975" fill="none" />
    <path id="current-power-arrow-path-load"
      d="m118 103.82v38.495c0 3.415 1.0474 6.577 2.5063 8.1595 0 0 2.2897 4.1037 9.416 4.1037h34.975" fill="none" />
    <g>
      <path id="current-power-box-inverter" x="80" y="70" width="50" height="50" ry="7"
        d="m87.464 70.49h35.072c3.8636 0 6.9739 3.1104 6.9739 6.9739v35.072c0 3.8636-3.1104 6.9739-6.9739 6.9739h-35.072c-3.8636 0-6.9739-3.1104-6.9739-6.9739v-35.072c0-3.8636 3.1104-6.9739 6.9739-6.9739z"
        class="current-power-box" />
      <path id="current-power-box-grid" x="150" y="10" width="50" height="50" ry="7"
        d="m157.46 10.49h35.072c3.8636 0 6.9739 3.1104 6.9739 6.9739v35.072c0 3.8636-3.1104 6.9739-6.9739 6.9739h-35.072c-3.8636 0-6.9739-3.1104-6.9739-6.9739v-35.072c0-3.8636 3.1104-6.9739 6.9739-6.9739z"
        class="current-power-box" />
      <path id="current-power-box-load" x="150" y="130" width="50" height="50" ry="7"
        d="m157.46 130.49h35.072c3.8636 0 6.9739 3.1104 6.9739 6.9739v35.072c0 3.8636-3.1104 6.9739-6.9739 6.9739h-35.072c-3.8636 0-6.9739-3.1104-6.9739-6.9739v-35.072c0-3.8636 3.1104-6.9739 6.9739-6.9739z"
        class="current-power-box" />
      <path id="current-power-box-pv" x="10" y="10" width="50" height="50" ry="7"
        d="m17.464 10.49h35.072c3.8636 0 6.9739 3.1104 6.9739 6.9739v35.072c0 3.8636-3.1104 6.9739-6.9739 6.9739h-35.072c-3.8636 0-6.9739-3.1104-6.9739-6.9739v-35.072c0-3.8636 3.1104-6.9739 6.9739-6.9739z"
        class="current-power-box" />
      <path id="current-power-box-battery" x="10" y="130" width="50" height="50" ry="7"
        d="m17.464 130.49h35.072c3.8636 0 6.9739 3.1104 6.9739 6.9739v35.072c0 3.8636-3.1104 6.9739-6.9739 6.9739h-35.072c-3.8636 0-6.9739-3.1104-6.9739-6.9739v-35.072c0-3.8636 3.1104-6.9739 6.9739-6.9739z"
        class="current-power-box" />
      <text id="current-power-label-inverter" x="105" y="80">
        <tspan x="105" y="80" class="current-power-label-text">Inverter</tspan>
      </text>
      <text id="current-power-label-grid" x="175" y="20">
        <tspan x="175" y="20" class="current-power-label-text">Grid</tspan>
      </text>
      <text id="current-power-label-load" x="175" y="140">
        <tspan x="175" y="140" class="current-power-label-text">Load</tspan>
      </text>
      <text id="current-power-label-pv" x="35" y="20">
        <tspan x="35" y="20" class="current-power-label-text">PV</tspan>
      </text>
      <text id="current-power-pv" x="51.6" y="31.3">
        <tspan x="51.6" y="31.3" class="current-power-text">9999 W</tspan>
      </text>
      <text id="current-power-grid" x="191.6" y="31.3">
        <tspan x="191.6" y="31.3" class="current-power-text">-9999 W</tspan>
      </text>
      <text id="current-power-load" x="191.6" y="151.3">
        <tspan x="191.6" y="151.3" class="current-power-text">9999 W</tspan>
      </text>
      <text id="current-power-battery" x="51.6" y="151.3">
        <tspan x="51.6" y="151.3" class="current-power-text">-9999 W</tspan>
      </text>
      <text id="current-power-soc" x="46.8" y="161.3">
        <tspan x="46.8" y="161.3" class="current-power-text">100%</tspan>
      </text>
      <text id="current-power-label-battery" x="35" y="139.6">
        <tspan x="35" y="139.6" class="current-power-label-text">Battery</tspan>
      </text>
      <rect id="current-power-bar-pv" x="14" y="22" width="4" height="15" class="current-power-bar" />
      <rect id="current-power-bar-grid" x="154" y="22" width="4" height="15" class="current-power-bar" />
      <rect id="current-power-bar-load" x="154" y="142" width="4" height="15" class="current-power-bar" />
      <rect id="current-power-bar-battery" x="14" y="142" width="4" height="15" class="current-power-bar" />
      <rect id="current-power-bar-soc" x="27.5" y="164.5" width="15" height="4" class="current-power-bar" />
      <path id="current-power-arrow-pv"
        d="m54.304 25h1.569l-0.0013 3.1201h1.0001l-1.7832 3.2692-1.7888-3.2692h1.0001l0.0041-3.1201"
        style="fill:#fefe7f" />
      <path id="current-power-arrow-grid-sell"
        d="m194.3 31.352h1.569l-1e-3 -3.1201h1.0001l-1.7832-3.2692-1.7888 3.2692h1.0001l4e-3 3.1201"
        style="fill:#95fe7f" />
      <path id="current-power-arrow-grid-buy"
        d="m194.3 24.963h1.5689l-1e-3 3.1198h1l-1.783 3.2689-1.7887-3.2689h1l4e-3 -3.1198" style="fill:#fe7f7f" />
      <path id="current-power-arrow-load" d="m194.3 145h1.5689l-1e-3 3.1198h1l-1.783 3.2689-1.7887-3.2689h1l4e-3 -3.1198"
        style="fill:#fe7f7f" />
      <path id="current-power-arrow-battery-discharge"
        d="m54.304 151.39h1.569l-0.0013-3.1201h1.0001l-1.7832-3.2692-1.7888 3.2692h1.0001l0.0041 3.1201"
        style="fill:#fe7f7f" />
      <path id="current-power-arrow-battery-charge"
        d="m54.304 145h1.5689l-0.0013 3.1198h1l-1.783 3.2689-1.7887-3.2689h1l0.0041-3.1198" style="fill:#95fe7f" />
      <path
        d="m60.006 157.3h20.487c7.1263 0 10.55-4.1453 10.55-4.1453 1.4589-1.5825 3.3139-4.703 3.3139-8.118v-25.04m-5.7768 2e-3v25.038c-0.76682 2.6285-2.6287 6.3887-8.0867 6.3887h-20.487"
        style="fill:none;stroke:url(#linearGradientPipeBattery)" />
      <path
        d="m150 157.29h-20.457c-7.1263 0-10.55-4.1453-10.55-4.1453-1.4589-1.5825-3.3139-4.703-3.3139-8.118v-25.036m5.7768 5e-3v25.031c0.76682 2.6285 2.6287 6.3887 8.0868 6.3887h20.457"
        style="fill:none;stroke:url(#linearGradientPipeLoad)" />
      <path
        d="m150 31.352h-20.458c-7.1263 0-10.55 4.1453-10.55 4.1453-1.4589 1.5825-3.3139 4.703-3.3139 8.118v26.381m5.7768 0.0075v-26.388c0.76682-2.6285 2.6287-6.3887 8.0868-6.3887h20.473"
        style="fill:none;stroke:url(#linearGradientPipeGrid)" />
      <path
        d="m60.001 31.352h19.983c7.1263 0 10.55 4.1453 10.55 4.1453 1.4589 1.5825 3.3139 4.703 3.3139 8.118v26.381m-5.7768 0.0075v-26.388c-0.76682-2.6285-2.6287-6.3887-8.0868-6.3887h-19.998"
        style="fill:none;stroke:url(#linearGradientPipePV)" />
    </g>
  </svg>
</template>

<style scoped>
svg text {
  fill: var(--color-text);
}

.current-power-box {
  fill: var(--color-background-mute);
  stroke: var(--color-border);
}

.current-power-label-text {
  font-size: 6.35px;
  stroke-width: .26458;
  text-align: center;
  text-anchor: middle;
}

.current-power-text {
  font-size: 8.4667px;
  stroke-width: .26458;
  text-align: end;
  text-anchor: end;
}

.current-power-bar {
  fill: none;
  stroke-linecap: square;
  stroke-linejoin: round;
  stroke-width: .19834;
  stroke: var(--color-border);
}
</style>
