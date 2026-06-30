document.getElementById('extract-btn').addEventListener('click', async function() {
    const urlInput = document.getElementById('news-url').value.trim();
    const resultBox = document.getElementById('result-box');
    const extractBtn = document.getElementById('extract-btn');

    if (!urlInput) {
        alert('Por favor, ingresá una URL válida.');
        return;
    }

    // Efecto visual de carga
    extractBtn.innerText = 'PROCESANDO...';
    extractBtn.disabled = true;

    try {
        // Hacemos la petición real a nuestra API de Python local
        const respuesta = await fetch('http://127.0.0.1:5000/api/extraer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: urlInput })
        });

        const datos = await respuesta.json();

        if (datos.error) {
            alert('Error al extraer: ' + datos.error);
        } else {
            // Elementos del DOM
            const resTitle = document.getElementById('res-title');
            const resImageContainer = document.getElementById('res-image-container');
            const resText = document.getElementById('res-text');

            // 1. Inyectamos el Título Real
            resTitle.innerText = datos.titulo;
            
            // 2. Inyectamos la Imagen Real (si existe)
            if (datos.imagenes && datos.imagenes.length > 0) {
                resImageContainer.innerHTML = `<img src="${datos.imagenes[0]}" alt="Portada">`;
                resImageContainer.classList.remove('hidden');
            } else {
                resImageContainer.innerHTML = '';
                resImageContainer.classList.add('hidden');
            }
            
            // 3. Inyectamos TODOS los párrafos reales de forma dinámica
            resText.innerHTML = datos.cuerpo.map(parrafo => `<p>${parrafo}</p>`).join('');

            // Mostramos el recuadro de resultados
            resultBox.classList.remove('hidden');
            resultBox.scrollIntoView({ behavior: 'smooth' });
        }

    } catch (error) {
        console.error(error);
        alert('No se pudo conectar con el servidor de Python. Asegurate de que esté corriendo.');
    } finally {
        // Restauramos el botón
        extractBtn.innerText = 'EXTRAER';
        extractBtn.disabled = false;
    }
});