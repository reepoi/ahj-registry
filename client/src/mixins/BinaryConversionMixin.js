export default {
    methods: {
        convertBinaryToPhoto(binaryString) {
            var binary = atob(binaryString.replace(/\s/g, ''));
            var len = binary.length;
            var buffer = new ArrayBuffer(len);
            var view = new Uint8Array(buffer);
            for (var i = 0; i < len; i++) {
                view[i] = binary.charCodeAt(i);
            }
            var blob = new Blob( [view], { type: "image/jpeg" });
            let objURL = URL.createObjectURL(blob);
            return objURL;
          }
    }
}