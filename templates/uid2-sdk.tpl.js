class UID2 {
    constructor() {
        this.init = (identity) => {
            if (identity) {
                this.setIdentity(identity);
            }
            else {
                this.refreshIfNeeded();
            }
        };
        this.getIdentity = () => {
            const payload = this.getCookie("__uid_2");
            if (payload) {
               return JSON.parse(payload);
            }
        };
        this.getAdvertisingToken = () => {
            const identity = this.getIdentity();
            if (identity && "body" in identity) {
                return identity["body"]["advertising_token"];
            }
        };
        this.getRefreshToken = () => {
            const identity = this.getIdentity();
            if (identity && "body" in identity) {
                return identity["body"]["refresh_token"];
            }
        };
        
        this.setIdentity = (value) => {
            var payload;
            if (typeof (value) === "object") {
                payload = JSON.stringify(value);
            }
            else {
                payload = value;
            }
            this.setCookie("__uid_2", payload);
        };
        this.setCookie = (name, value) => {
            var days = 7;
            var date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            document.cookie = name + "=" + encodeURIComponent(value) + " ;path=/;expires=" + date.toUTCString();
        };
        this.getCookie = (name) => {
            const docCookie = document.cookie;
            if (docCookie) {
                var payload = docCookie.split("; ").find(row => row.startsWith(name));
                if (payload) {
                    return decodeURIComponent(payload.split("=")[1]);
                }
            }
            else {
                return undefined;
            }
        };
        this.removeCookie = (name) => {
            document.cookie = name + "=;path=/;expires=Tue, 1 Jan 1980 23:59:59 GMT";
        };

        this.normalize_email = (email) => {
            email = email.trim().toLowerCase();
            var parts = email.split("@");
            if (parts[1] == "gmail.com") {
                const regex = /\./i;
                parts[0] = parts[0].replace(regex, "").split("+")[0];
                email = parts.join("@");
            }
            return email;
        };
        this.base64_encoded_sha256 = async (str) => {
            const buffer = new Uint8Array([].map.call(str, (c) => c.charCodeAt(0))).buffer;
            const digest = await window.crypto.subtle.digest("SHA-256", buffer);
            return window.btoa(String.fromCharCode(...new Uint8Array(digest)));
        };
        this.handleResponse = (resp) => {
            this.setIdentity(resp);
        };

        this.connect = (email) => {
            this.base64_encoded_sha256(this.normalize_email(email)).then(email_hash => {
                const url = "{{ base_url }}/token/generate?email_hash=" + encodeURIComponent(email_hash);
                const req = new XMLHttpRequest();
                req.overrideMimeType("application/json");
                var cb = this.handleResponse;
                req.open("GET", url, false);
                req.onload = function () {
                    cb(req.responseText);
                };
                req.send();
            });
        };
        this.refreshIfNeeded = () => {
            const refresh_token = this.getRefreshToken();
            if (refresh_token) {
                const url = "{{ base_url }}/token/refresh?refresh_token=" + encodeURIComponent(refresh_token);
                const req = new XMLHttpRequest();
                req.overrideMimeType("application/json");
                var cb = this.handleResponse;
                req.open("GET", url, false);
                req.onload = function () {
                    cb(req.responseText);
                };
                req.send();
            }
        };
        this.disconnect = () => {
            this.removeCookie("__uid_2");
        };
    }
}
window.__uid2 = new UID2();
