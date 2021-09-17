ClassicEditor
    .create(document.querySelector('#message'), {
        toolbar: {
            items: [
                'undo',
                'redo',
                '|',
                'fontFamily',
                'fontSize',
                'fontColor',
                '|',
                'bold',
                'italic',
                'underline',
                'horizontalLine',
                '|',
                'alignment',
                'bulletedList',
                'numberedList',
                'indent',
                'outdent',
                '|',
                'blockQuote',
                'link',
                'removeFormat'
            ]
        },
        language: 'zh'
    })
    .then(editor => {
        window.editor = editor;
    });

let droppable = $(".dad-selector").dad({
    placeholderTarget: ".item"
});

$(".area-delete").on("dadDrop", function (e, element) {
    $(element).remove();
});

$('#add').on('click', function () {
    let newElement = document.createElement("div");
    let value = document.getElementById('add-attr').value;
    value = value.replace(/\s+/g, '');
    if (value.length >= 2) {
        newElement.innerHTML = '<div class="item"><span>' + value + '</span></div>';
        $("#attr-cloud").append(newElement);
    } else {
        alert('The length of attribute should not less than 2')
    }
    document.getElementById('add-attr').value = "";
})

let attrs_list = document.getElementById('attr-cloud');
function push_to_parser(str) {
    if (str.length == 0) {
        attrs_list.innerHTML = '';
    } else {
        axios.get('/parse?subject=' + str)
            .then(function (response) {
                attrs_list.innerHTML = '';
                for (const attr of response.data.response) {
                    let newElement = document.createElement("div");
                    newElement.innerHTML = '<div class="item"><span>' + attr + '</span></div>';
                    $("#attr-cloud").append(newElement);
                }
            })
            .catch(function (error) {
                console.log(error);
            });
    }
}

function get_AttrsList() {
    const attrs_div = document.querySelectorAll("div.item span");
    let values = [];
    attrs_div.forEach((attr) => {
        values.push(attr.textContent);
    });
    for (let i = 0; i < values.length; i++) {
        if (i == 0) {
            document.getElementById('AttrsList').value += values[i];
        } else {
            document.getElementById('AttrsList').value += ',' + values[i];
        }
    }
    return true;
}

$('#upload').on('click', function (e) {
    e.preventDefault();
    $('#file-uploader').trigger('click');
});

const fileUploader = document.querySelector('#file-uploader');
fileUploader.addEventListener('change', (event) => {
    const files = event.target.files;
    for (const file of files) {
        const name = file.name;
        const size = ~~((file.size) / 1024);
        const msg = '<li><i class="fa fa-file-o" aria-hidden="true"></i> ' + name + '<span\
                        class="text-muted tx-11"> (' + size + ' KB)</span></li>';
        $('.att-list').append(msg);
    }
});

$('#cancel').on('click', function (e) {
    $('#file-uploader').value = "";
    $('.att-list').empty();
});
