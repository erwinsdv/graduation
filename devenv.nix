{
  pkgs,
  ...
}:

{
  languages.java.enable = true;
  packages = [
    pkgs.graphviz
  ];

  enterShell = ''
    echo -e "\n\033[1;32m✔ Hello java\033[0m"
    java --version
  '';
}
