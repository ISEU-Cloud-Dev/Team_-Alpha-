async function cargarDashboard() {
    try {
        const res = await fetch('/api/v1/dashboard/');
        const data = await res.json();

        document.getElementById('kpi-links').textContent = data.total_links_activos;
        document.getElementById('kpi-clicks').textContent = data.total_clicks_globales;
        document.getElementById('kpi-activos').textContent = data.total_links_activos;
        dibujarLineChart('grafico-clicks-dia', data.clicks_por_dia);
        dibujarPieChart('grafico-paises', data.top_paises);
    } catch (err) {
        console.error('Error cargando dashboard:', err);
    }
}

async function cargarUrls() {
    try {
        const res = await fetch('/api/v1/shorten/');
        const links = await res.json();
        const tbody = document.getElementById('tabla-urls-body');

        if (links.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Aún no hay URLs creadas.</td></tr>';
            return;
        }

        tbody.innerHTML = links.map(link => `
            <tr>
                <td><span class="badge-corto">${link.url_corta}</span></td>
                <td><span class="url-larga" title="${link.url_larga}">${link.url_larga}</span></td>
                <td>${link.fecha_creacion}</td>
                <td>${link.clicks}</td>
                <td>
                    <button class="action-btn" onclick="copiarUrl('${link.url_corta}')" title="Copiar enlace">Copiar</button>
                    <button class="action-btn action-btn-danger" onclick="eliminarUrl(${link.id})" title="Eliminar enlace">Eliminar</button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        console.error('Error cargando URLs:', err);
    }
}

function copiarUrl(codigo) {
    const url = `${window.location.origin}/api/v1/${codigo}`;
    navigator.clipboard.writeText(url).then(() => {
        alert('Enlace copiado: ' + url);
    });
}

async function eliminarUrl(id) {
    if (!confirm('¿Eliminar este enlace? Esta acción no se puede deshacer.')) return;
    try {
        const res = await fetch(`/api/v1/shorten/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Error al eliminar');
        cargarUrls();
        cargarDashboard();
    } catch (err) {
        console.error('Error eliminando URL:', err);
        alert('No se pudo eliminar el enlace.');
    }
}

// Gráfico de línea simple con Canvas nativo (clicks por día)
function dibujarLineChart(containerId, datos) {
    const container = document.getElementById(containerId);
    container.innerHTML = '<canvas></canvas>';
    const canvas = container.querySelector('canvas');
    const ctx = canvas.getContext('2d');

    const w = container.clientWidth;
    const h = container.clientHeight;
    canvas.width = w;
    canvas.height = h;

    const padding = 30;
    const maxClicks = Math.max(...datos.map(d => d.clicks), 1);
    const stepX = (w - padding * 2) / (datos.length - 1 || 1);

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = padding + ((h - padding * 2) / 4) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(w - padding, y);
        ctx.stroke();
    }

    const gradient = ctx.createLinearGradient(0, padding, 0, h - padding);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.35)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');

    ctx.beginPath();
    datos.forEach((d, i) => {
        const x = padding + stepX * i;
        const y = h - padding - (d.clicks / maxClicks) * (h - padding * 2);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.lineTo(padding + stepX * (datos.length - 1), h - padding);
    ctx.lineTo(padding, h - padding);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    ctx.beginPath();
    ctx.strokeStyle = '#818cf8';
    ctx.lineWidth = 2.5;
    datos.forEach((d, i) => {
        const x = padding + stepX * i;
        const y = h - padding - (d.clicks / maxClicks) * (h - padding * 2);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    datos.forEach((d, i) => {
        const x = padding + stepX * i;
        const y = h - padding - (d.clicks / maxClicks) * (h - padding * 2);
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#818cf8';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
    });

    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'center';
    datos.forEach((d, i) => {
        const x = padding + stepX * i;
        ctx.fillText(d.fecha.slice(5), x, h - 10);
    });
}

// Gráfico de pastel simple con Canvas nativo (clicks por país)
function dibujarPieChart(containerId, datos) {
    const container = document.getElementById(containerId);
    container.innerHTML = '<canvas></canvas>';
    const canvas = container.querySelector('canvas');
    const ctx = canvas.getContext('2d');

    const w = container.clientWidth;
    const h = container.clientHeight;
    canvas.width = w;
    canvas.height = h;

    if (!datos || datos.length === 0) {
        ctx.fillStyle = '#94a3b8';
        ctx.font = '13px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Sin datos aún', w / 2, h / 2);
        return;
    }

    const colores = ['#818cf8', '#a78bfa', '#f472b6', '#60a5fa', '#34d399'];
    const cx = w / 2 - 40;
    const cy = h / 2;
    const radio = Math.min(cx, cy) - 10;

    let anguloInicio = -Math.PI / 2;
    datos.forEach((d, i) => {
        const anguloFin = anguloInicio + (d.porcentaje / 100) * Math.PI * 2;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, radio, anguloInicio, anguloFin);
        ctx.closePath();
        ctx.fillStyle = colores[i % colores.length];
        ctx.fill();
        anguloInicio = anguloFin;
    });

    let legendY = 20;
    datos.forEach((d, i) => {
        ctx.fillStyle = colores[i % colores.length];
        ctx.fillRect(w - 90, legendY, 10, 10);
        ctx.fillStyle = '#ffffff';
        ctx.font = '11px Inter, sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(`${d.pais} (${d.porcentaje}%)`, w - 75, legendY + 9);
        legendY += 20;
    });
}

cargarDashboard();
cargarUrls();