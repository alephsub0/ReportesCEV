document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("formularioseguimiento").addEventListener("submit", function (event) {

        event.preventDefault();

        $('#NotificacionGeneracion').show();  // Mostrar el mensaje de procesamiento

        var formData = new FormData($(this)[0]);

        $.ajax({
            url: $(this).attr('action'),
            type: $(this).attr('method'),
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                // Procesamiento exitoso, mostrar el enlace de descarga
                $('#NotificacionGeneracion').hide();
                // de la respuesta mostramos status

                if (response.status == 'success') {
                    url = UrlDescarga.slice(0, -1) + response.code;

                    $('#NotificacionDescarga').html('<p style="margin-bottom: 0;"> Sus reportes están listos, los puede descargar en el siguiente enlace: <a href="' + url + '" class="btn btn-success" role="button">Descargar Reporte</a> </p>');
                    $('#NotificacionDescarga').show();
                }
                else {
                    alert("Error al generar el reporte." + response.message);
                }
            },
            error: function (xhr, errmsg, err) {
                alert("Error al generar el reporte. Por favor, inténtelo de nuevo. Si el problema persiste, contacte al administrador del sistema." + xhr.status + ": " + xhr.responseText + ". " + errmsg + ". " + err);
                // Recargamos la página
                location.reload();
            }
        });
    });
});
