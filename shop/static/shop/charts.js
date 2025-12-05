// Simple Charts Library
(function() {
  
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

  // ==================== BAR CHART ====================
  window.createBarChart = function(canvas, items, options) {
    options = options || {};
    const cfg = {
      barColor: options.barColor || '#1e40af',
      fillColor: options.fillColor || 'rgba(59,130,246,0.12)',
      hoverColor: options.hoverColor || '#1e3a8a',
      gridColor: options.gridColor || '#eef6ff',
      bg: options.bg || '#ffffff',
      padding: options.padding || {left:48, right:20, top:20, bottom:48},
    };

    const ctx = canvas.getContext('2d');
    const tooltip = createTooltip();
    
    const points = (items || []).map((it) => ({
      date: it.date,
      label: it.date,
      value: Number(it.value),
    }));

    function draw() {
      fitCanvas(canvas);
      const dpr = canvas._dpr || 1;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const W = canvas.width / dpr;
      const H = canvas.height / dpr;
      ctx.clearRect(0, 0, W, H);

      ctx.fillStyle = cfg.bg;
      ctx.fillRect(0, 0, W, H);

      if (!points.length) return;

      const pad = cfg.padding;
      const plotW = W - pad.left - pad.right;
      const plotH = H - pad.top - pad.bottom;

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

      // Grid
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

      // Bars
      for (let i=0;i<points.length;i++){
        const left = xLeftFor(i);
        const topY = yFor(points[i].value);
        const bottomY = pad.top + plotH;
        const h = Math.max(0.5, bottomY - topY);

        ctx.beginPath();
        ctx.rect(left + 0.5, topY, barW, h);
        ctx.fillStyle = cfg.fillColor;
        ctx.fill();

        ctx.beginPath();
        ctx.rect(left + 0.5, topY, barW, h);
        ctx.fillStyle = cfg.barColor;
        ctx.globalAlpha = 0.95;
        ctx.fill();
        ctx.globalAlpha = 1;
      }

      // Labels
      ctx.fillStyle = '#475569';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.font = '11px system-ui, Arial';
      const minLabelSpacing = 50;
      const maxLabelsCount = Math.floor(plotW / minLabelSpacing);
      const optimalStep = Math.max(1, Math.ceil(points.length / Math.max(1, maxLabelsCount)));
      
      for (let i=0; i<points.length; i++){
        if (i % optimalStep === 0 || i === points.length - 1){
          const x = xFor(i);
          const shortDate = points[i].label.split('.').slice(0,2).join('.');
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

      if (hovered === -1){ tooltip.style.display = 'none'; return; }

      tooltip.style.display = 'block';
      tooltip.innerText = points[hovered].label + ' — ' + points[hovered].value.toString();
      tooltip.style.left = (e.clientX) + 'px';
      tooltip.style.top = (e.clientY - 12) + 'px';
    }

    function onLeave(){ 
      tooltip.style.display = 'none'; 
    }

    draw();
    canvas.addEventListener('mousemove', onMove);
    canvas.addEventListener('mouseleave', onLeave);
    window.addEventListener('resize', draw);

    return { redraw: draw };
  };

  // ==================== PIE CHART ====================
  window.createPieChart = function(canvas, items, options) {
    options = options || {};
    const cfg = {
      colors: options.colors || ['#1e40af', '#3b82f6', '#7c3aed', '#db2777', '#f59e0b'],
      bg: options.bg || '#ffffff',
      textColor: options.textColor || '#1f2937'
    };

    const ctx = canvas.getContext('2d');
    const tooltip = createTooltip();

    const points = (items || []).map((it, idx) => ({
      label: it.label || it.name || ('Item ' + idx),
      value: Number(it.value) || 0,
      color: cfg.colors[idx % cfg.colors.length]
    }));

    console.log('createPieChart called with points:', points);

    function draw() {
      fitCanvas(canvas);
      const dpr = canvas._dpr || 1;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const W = canvas.width / dpr;
      const H = canvas.height / dpr;

      ctx.fillStyle = cfg.bg;
      ctx.fillRect(0, 0, W, H);

      if (!points || points.length === 0) {
        console.log('No points to draw');
        return;
      }

      const total = points.reduce((s, p) => s + p.value, 0);
      console.log('Total value:', total);
      
      if (total <= 0) {
        console.log('Total is zero or negative');
        return;
      }

      const cx = W * 0.35;
      const cy = H * 0.4;
      const r = Math.min(W, H) * 0.25;

      console.log('Drawing pie at', cx, cy, 'radius', r);

      let angle = -Math.PI / 2;

      for (let i = 0; i < points.length; i++) {
        const sliceSize = (points[i].value / total) * 2 * Math.PI;

        ctx.beginPath();
        ctx.arc(cx, cy, r, angle, angle + sliceSize);
        ctx.lineTo(cx, cy);
        ctx.fillStyle = points[i].color;
        ctx.fill();

        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();

        angle += sliceSize;
      }

      // Legend
      ctx.font = '12px Arial';
      ctx.fillStyle = cfg.textColor;
      ctx.textAlign = 'left';

      const legendX = cx + r + 30;
      const legendY = cy - points.length * 10;

      for (let i = 0; i < points.length; i++) {
        const y = legendY + i * 22;

        ctx.fillStyle = points[i].color;
        ctx.fillRect(legendX, y, 12, 12);

        ctx.fillStyle = cfg.textColor;
        const pct = ((points[i].value / total) * 100).toFixed(1);
        ctx.fillText(points[i].label + ' ' + points[i].value + ' (' + pct + '%)', legendX + 18, y + 10);
      }

      console.log('Pie chart drawn');
    }

    function onMove(e) {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const dpr = canvas._dpr || 1;
      const W = canvas.width / dpr;
      const H = canvas.height / dpr;

      const cx = W * 0.35;
      const cy = H * 0.4;
      const r = Math.min(W, H) * 0.25;

      const dx = x - cx;
      const dy = y - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist > r) {
        tooltip.style.display = 'none';
        return;
      }

      const total = points.reduce((s, p) => s + p.value, 0);
      let currentAngle = -Math.PI / 2;
      let hoveredIdx = -1;

      for (let i = 0; i < points.length; i++) {
        const sliceSize = (points[i].value / total) * 2 * Math.PI;
        let angle = Math.atan2(dy, dx);
        if (angle >= currentAngle - Math.PI / 2 && angle <= currentAngle + sliceSize - Math.PI / 2) {
          hoveredIdx = i;
          break;
        }
        currentAngle += sliceSize;
      }

      if (hoveredIdx >= 0) {
        tooltip.style.display = 'block';
        const pct = ((points[hoveredIdx].value / total) * 100).toFixed(1);
        tooltip.innerText = points[hoveredIdx].label + ': ' + points[hoveredIdx].value + ' (' + pct + '%)';
        tooltip.style.left = e.clientX + 'px';
        tooltip.style.top = (e.clientY - 12) + 'px';
      } else {
        tooltip.style.display = 'none';
      }
    }

    function onLeave() {
      tooltip.style.display = 'none';
    }

    draw();
    canvas.addEventListener('mousemove', onMove);
    canvas.addEventListener('mouseleave', onLeave);
    window.addEventListener('resize', draw);

    return { redraw: draw };
  };

})();
