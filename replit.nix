{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.nodejs_18
    pkgs.postgresql_15
  ];
  
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.glib
      pkgs.xsimd
      pkgs.util-linux
    ];
    PYTHONPATH = "/home/runner/NXTRIX-CRM";
    STREAMLIT_SERVER_PORT = "8080";
    STREAMLIT_SERVER_ADDRESS = "0.0.0.0";
  };
}