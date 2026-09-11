/* Display ads. Leave enabled:false until AdSense/Carbon is approved.
   Then set adsenseClient to ca-pub-XXXXXXXXXXXXXXXX and enabled:true, rebuild. */
window.RBDB_ADS = {
  enabled: false,
  adsenseClient: "",
  adsenseAutoAds: false,
  carbonServe: "",
  carbonPlacement: ""
};

/* Extra affiliate IDs. TCGplayer + Amazon are already live in tcgplayer-config.js and Shop.
   Fill these after approval; empty IDs still open the catalog, just without tracking. */
window.RBDB_AFFILIATES = {
  cardmarketId: "",
  ebayCampId: "",
  cardnexusUrl: ""
};
