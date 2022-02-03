<script>
function __init()
{

    $('#search_input')
        .val('') ///Borramos cualquier valor que haya previo a la carga de la pagina
        .focus() ///Ponemos el foco en el input
        .keyup(function(){ ///Evento de presionar una tecla

            if(!$.trim($(this).val())) ///Trim remueve los espacos en blanco al inicio y al final de la cadena
                $('.results .error').empty().hide(); ///Creo q aqui se crea el objeto results.error

        });

    var cache = {};
    ///alert("bu");
    $('#search_input').autocomplete({ ///Autocompleta el campo mientras se escribe
        minLength: 2, ///El minimo de caracteres que se deben typear para iniciar el autocomplete
        select: function( event, ui ) { ///Select actualiza el valor del input con el elemento seleccionado
            return false;
        },
        open: function() { ///Evento que se activa cuando el menu es abierto o actualizado
            $('.results .wrapper').html($(this).autocomplete("widget").html());
            $(this).autocomplete("widget").hide();
        },
        source: function( request, response ) { ///El origen de datos a sugerir, request tiene el valor ingresado hsata el moemnto, response es la solicitu de la lista a sugerir

            if (cache[request.term]) {
                response(cache[request.term]);
                return;
            }

            $.ajax({
                dataType : 'json',
                method : 'POST',
                url : 'ajax/search/',
                data : {
                    q : encodeURIComponent(request.term),
                    csrfmiddlewaretoken : $('input[name=csrfmiddlewaretoken]').val()
                },
                success : function(data) {
                    var productos = [];

                    for(var x in data)
                    {
                      console.log(data[x].fields['nombre']);
                      ///alert("aqui toi apa",data[0].nombre)
                        productos.push({
                            nombre : data[x].fields['nombre'],
                            empresa : data[x].fields['empresa'],
                            beneficio : data[x].fields['beneficio']
                        });
                    }

                    cache[request.term] = productos;
                    console.log(productos);
                    response(productos);
                },
                error : function(message) {
                        console.log(message);
                     }
            });
        },
        response: function(event, ui) {

            if (ui.content.length === 0) {
                $('.results .error').html('No se encontraron resultados').show();
                $('.results .wrapper').empty();
            }
            else
                $('.results .error').empty().hide();
        }
    }).autocomplete('instance')._renderItem = function(ul, item) {
    ///.autocomplete('instance')._renderItem = function(ul, item) {
    console.log("renderizando...");
        var producto_tmpl = $('</div>')
                        .addClass('producto')
                        .append('<a href="/" />').find('a').addClass('nombre').html(item.nombre)
                        .parent()
                        .append('<span class="identity"><strong>Empresa:</strong><span></span></span>')
                        .find('.empresa > span').append(item.empresa)
                        .parent().parent()
                        .append('<span class="email"><strong>Beneficio:</strong><span></span></span>')
                        .find('.beneficio > span').append(item.beneficio)
                        .parent().parent();
        return $('<div></div>')
            .data('item.autocomplete', item)
            .append(producto_tmpl)
            .appendTo(ul);
    };
}

$(document).ready(__init);
</script>
