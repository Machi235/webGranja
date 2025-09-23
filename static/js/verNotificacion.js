function toggleNotificaciones() {
    document.getElementById("notiPanel").classList.toggle("show");
}

document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.marcar-leida');
  if (!btn) return;

  const id = btn.dataset.id;
  const url = btn.dataset.url || `/notificaciones/marcar_leida/${id}`;

  console.log('Intentando marcar noti:', id, 'url:', url);

  try {
    btn.disabled = true;

    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
        // si usas CSRF añade la cabecera correspondiente aquí
      }
    });

    console.log('Fetch status:', resp.status, 'content-type:', resp.headers.get('content-type'));

    // Si el servidor devuelve error HTTP, leer el texto para ver el motivo
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`Server returned ${resp.status}: ${text}`);
    }

    // Parsear JSON sólo si el content-type lo indica, si no intentar parsear fallback
    const ct = (resp.headers.get('content-type') || '').toLowerCase();
    let data;
    if (ct.includes('application/json')) {
      data = await resp.json();
    } else {
      const text = await resp.text();
      try {
        data = JSON.parse(text);
      } catch (err) {
        console.warn('Respuesta no JSON:', text);
        data = null;
      }
    }

    console.log('Response data:', data);

    if (data && data.success) {
      // Eliminar la notificación del DOM
      const noti = document.getElementById(`noti-${id}`);
      if (noti) noti.remove();

      // Actualizar el badge con seguridad
      const badge = document.getElementById('notiBadge');
      if (badge) {
        let count = parseInt((badge.textContent || '').trim(), 10) || 0;
        count = Math.max(0, count - 1);
        if (count === 0) {
          badge.style.display = 'none';
          badge.textContent = '';
        } else {
          badge.style.display = ''; // por si estaba oculto
          badge.textContent = count;
        }
      }
    } else {
      throw new Error('Respuesta inválida del servidor o data.success=false');
    }

  } catch (err) {
    console.error('Error al marcar notificación:', err);
    alert('Error al marcar notificación. Revisa la consola y Network.');
    btn.disabled = false;
  }
});
