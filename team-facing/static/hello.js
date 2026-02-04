
// Fetch from the vs folder an editor file
require(["vs/editor/editor.main"], function () {
  window.editor = monaco.editor.create(
    document.getElementById("editor"),
    {
      value: `print("Hello Game Jam!")`,
      language: "python",
      theme: "vs-dark",
      automaticLayout: true
    }
  );
});
