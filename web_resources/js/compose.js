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
