//config.js
KindEditor.ready(function (K) {
    //通过浏览器调试查看富文本相关信息，如id，name
    window.editor = K.create('textarea[name=content]', {
        allowPreviewEmoticons: false,
        allowImageRemote: true,
        resizeType: 2,
        uploadJson: '/admin/upload/kindeditor', //这个是上传图片后台处理的url
        width: '1200px',
        height: '700px',
    });
});
