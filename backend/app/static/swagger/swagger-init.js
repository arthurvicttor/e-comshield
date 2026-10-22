window.addEventListener("load", function () {
  window.ui = SwaggerUIBundle({
    url: "/openapi.json",
    dom_id: "#swagger-ui",
    deepLinking: true,
    showExtensions: true,
    showCommonExtensions: true,
    persistAuthorization: false,
    oauth2RedirectUrl: window.location.origin + "/docs/oauth2-redirect",
    presets: [SwaggerUIBundle.presets.apis],
    layout: "BaseLayout",
  });
});
