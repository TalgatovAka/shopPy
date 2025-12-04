/*
  Custom Canvas Chart Library: createBarChart
  - canvas: HTMLCanvasElement
  - items: [{date: 'DD.MM.YYYY', value: number}, ...]
  - options: { barColor, fillColor, hoverColor, gridColor, dateFormat }

  Draws a vertical bar chart with grid, axes and a hover tooltip.
  No external dependencies.
*/
(function(){
  function parseDateDMY(s) {
    // expects DD.MM.YYYY
    const parts = (s||'').split('.');
    if (parts.length !== 3) return new Date(s);
    return new Date(parseInt(parts[2],10), parseInt(parts[1],10)-1, parseInt(parts[0],10));
  }

  function createTooltip() {
    const t = document.createElement('div');
    t.style.position = 'fixed';
    t.style.pointerEvents = 'none';
    t.style.padding = '8px 10px';
    t.style.background = 'rgba(15,23,42,0.95)';
    t.style.color = 'white';
    t.style.borderRadius = '6px';
    t.style.fontSize = '13px';
    t.style.fontWeight = '700';
    t.style.transform = 'translate(-50%, -120%)';
    t.style.zIndex = 9999;
    t.style.display = 'none';
    document.body.appendChild(t);
    return t;
  }

  function fitCanvas(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.round(rect.width * dpr);
    canvas.height = Math.round(rect.height * dpr);
    canvas._dpr = dpr;
  }

  // Draws a vertical bar chart based on items
  function createBarChart(canvas, items, options) {
    options = options || {};
    const cfg = {
      barColor: options.barColor || '#1e40af',
      fillColor: options.fillColor || 'rgba(59,130,246,0.12)',
      hoverColor: options.hoverColor || '#1e3a8a',
      gridColor: options.gridColor || '#eef6ff',
      bg: options.bg || '#ffffff',
      padding: options.padding || {left:48, right:20, top:20, bottom:48},
      dateFormat: options.dateFormat || 'DD.MM.YYYY'
    };

    const ctx = canvas.getContext('2d');
    const tooltip = createTooltip();

    const points = (items || []).map((it) => {
      const d = parseDateDMY(it.date);
      return {date: d, label: it.date, value: Number(it.value)};
    });

    function draw() {
      fitCanvas(canvas);
      const dpr = canvas._dpr || 1;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const W = canvas.width / dpr;
      const H = canvas.height / dpr;
      ctx.clearRect(0,0,W,H);

      // background
      ctx.fillStyle = cfg.bg;
      ctx.fillRect(0,0,W,H);

      if (!points.length) return;

      const pad = cfg.padding;
      const plotW = W - pad.left - pad.right;
      const plotH = H - pad.top - pad.bottom;

      // scales
      const values = points.map(p => p.value);
      const vmin = Math.min.apply(null, values);
      const vmax = Math.max.apply(null, values);
      const vpad = Math.max(10, Math.round((vmax - vmin) * 0.12));
      const yMin = Math.max(0, vmin - vpad);
      const yMax = vmax + vpad;

      const barFullWidth = plotW / points.length;
      const barW = Math.max(6, Math.floor(barFullWidth * 0.6));

      function xFor(i) {
        return pad.left + i * barFullWidth + (barFullWidth - barW) / 2 + barW/2;
      }
      function xLeftFor(i){
        return pad.left + i * barFullWidth + (barFullWidth - barW) / 2;
      }
      function yFor(v) {
        const t = (v - yMin) / (yMax - yMin);
        return pad.top + (1 - t) * plotH;
      }

      // horizontal grid
      ctx.strokeStyle = cfg.gridColor;
      ctx.lineWidth = 1;
      ctx.beginPath();
      const gridCount = 4;
      ctx.font = '12px system-ui, Arial';
      ctx.fillStyle = '#6b7280';
      for (let i=0;i<=gridCount;i++){
        const gy = pad.top + (i / gridCount) * plotH;
        ctx.moveTo(pad.left, gy + 0.5);
        ctx.lineTo(W - pad.right, gy + 0.5);
        const val = Math.round(yMax - (i / gridCount) * (yMax - yMin));
        ctx.fillText(val.toString(), 8, gy + 4);
      }
      ctx.stroke();

      // bars
      for (let i=0;i<points.length;i++){
        const left = xLeftFor(i);
        const topY = yFor(points[i].value);
        const bottomY = pad.top + plotH;
        const h = Math.max(0.5, bottomY - topY);

        // fill (light)
        ctx.beginPath();
        ctx.rect(left + 0.5, topY, barW, h);
        ctx.fillStyle = cfg.fillColor;
        ctx.fill();

        // bar color (solid)
        ctx.beginPath();
        ctx.rect(left + 0.5, topY, barW, h);
        ctx.fillStyle = cfg.barColor;
        ctx.globalAlpha = 0.95;
        ctx.fill();
        ctx.globalAlpha = 1;

        // subtle border
        ctx.beginPath();
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(0,0,0,0.06)';
        ctx.rect(left + 0.5, topY, barW, h);
        ctx.stroke();
      }

      // x labels (adaptive: compute optimal spacing to prevent overlap)
      ctx.fillStyle = '#475569';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.font = '11px system-ui, Arial';
      
      // estimate: "DD.MM" is about 35-40px wide, add 10px margin = 50px min spacing
      const minLabelSpacing = 50;
      const maxLabelsCount = Math.floor(plotW / minLabelSpacing);
      const optimalStep = Math.max(1, Math.ceil(points.length / Math.max(1, maxLabelsCount)));
      
      for (let i=0; i<points.length; i++){
        if (i % optimalStep === 0 || i === points.length - 1){
          const x = xFor(i);
          const parts = points[i].label.split('.');
          // Format: DD.MM (no year)
          const shortDate = parts.length >= 2 ? (parts[0] + '.' + parts[1]) : points[i].label;
          ctx.fillText(shortDate, x, H - pad.bottom + 8);
        }
      }
    }

    function onMove(e){
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      if (!points.length) return;

      const pad = cfg.padding;
      const plotW = rect.width - pad.left - pad.right;
      const barFullWidth = plotW / points.length;
      let hovered = -1;
      for (let i=0;i<points.length;i++){
        const left = pad.left + i * barFullWidth + (barFullWidth - Math.max(6, Math.floor(barFullWidth*0.6))) / 2;
        const right = left + Math.max(6, Math.floor(barFullWidth*0.6));
        if (x >= left && x <= right){ hovered = i; break; }
      }

      if (hovered === -1){ tooltip.style.display = 'none'; draw(); return; }

      // position tooltip
      tooltip.style.display = 'block';
      tooltip.innerText = points[hovered].label + ' — ' + points[hovered].value.toString();
      tooltip.style.left = (e.clientX) + 'px';
      tooltip.style.top = (e.clientY - 12) + 'px';

      // redraw and highlight hovered bar
      draw();
      const dpr = canvas._dpr || 1;
      const W = canvas.width / dpr;
      const H = canvas.height / dpr;
      const barFullW = (W - pad.left - pad.right) / points.length;
      const left = pad.left + hovered * barFullW + (barFullW - Math.max(6, Math.floor(barFullW*0.6))) / 2;
      const topY = (function(){
        const values = points.map(p => p.value);
        const vmin = Math.min.apply(null, values);
        const vmax = Math.max.apply(null, values);
        const vpad = Math.max(10, Math.round((vmax - vmin) * 0.12));
        const yMin = Math.max(0, vmin - vpad);
        const yMax = vmax + vpad;
        const t = (points[hovered].value - yMin) / (yMax - yMin);
        const plotH = H - pad.top - pad.bottom;
        return pad.top + (1 - t) * plotH;
      })();
      const bottomY = pad.top + (H - pad.top - pad.bottom);
      const h = Math.max(0.5, bottomY - topY);

      const ctx2 = canvas.getContext('2d');
      ctx2.setTransform(dpr,0,0,dpr,0,0);
      // overlay highlight
      ctx2.beginPath();
      ctx2.fillStyle = cfg.hoverColor;
      ctx2.globalAlpha = 0.14;
      ctx2.rect(left + 0.5, topY, Math.max(6, Math.floor(barFullW*0.6)), h);
      ctx2.fill();
      ctx2.globalAlpha = 1;

      // value bubble above bar
      const cx = left + Math.max(6, Math.floor(barFullW*0.6)) / 2 + 0.5;
      const cy = topY - 10;
      const bw = 80; const bh = 30;
      const bx = cx - bw/2; const by = cy - bh/2;
      ctx2.fillStyle = 'rgba(15,23,42,0.95)';
      ctx2.beginPath();
      const r = 6;
      ctx2.moveTo(bx + r, by);
      ctx2.arcTo(bx + bw, by, bx + bw, by + bh, r);
      ctx2.arcTo(bx + bw, by + bh, bx, by + bh, r);
      ctx2.arcTo(bx, by + bh, bx, by, r);
      ctx2.arcTo(bx, by, bx + bw, by, r);
      ctx2.closePath();
      ctx2.fill();
      ctx2.fillStyle = '#fff';
      ctx2.font = '700 13px system-ui, Arial';
      ctx2.textAlign = 'center';
      ctx2.textBaseline = 'middle';
      ctx2.fillText(points[hovered].value.toString(), cx, cy);
    }

    function onLeave(){ tooltip.style.display = 'none'; draw(); }

    draw();
    canvas.addEventListener('mousemove', onMove);
    canvas.addEventListener('mouseleave', onLeave);
    window.addEventListener('resize', draw);

    return { redraw: draw, destroy: function(){ canvas.removeEventListener('mousemove', onMove); canvas.removeEventListener('mouseleave', onLeave); window.removeEventListener('resize', draw); if (tooltip && tooltip.parentNode) tooltip.parentNode.removeChild(tooltip); } };
  }

  window.createBarChart = createBarChart;

})();
