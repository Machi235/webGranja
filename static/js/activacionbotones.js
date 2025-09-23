
  document.querySelectorAll('.btn-check').forEach(radio => {
    radio.addEventListener('change', () => {
      document.querySelectorAll('.btn').forEach(btn => btn.classList.remove('active'));
      const label = document.querySelector(`label[for="${radio.id}"]`);
      if (label) label.classList.add('active');
    });
  });

