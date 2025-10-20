document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("namespaceForm");

  form.addEventListener("submit", function (event) {
    const cores = parseInt(document.getElementById("cores").value);
    const memoria = parseInt(document.getElementById("memoria").value);
    const io = parseInt(document.getElementById("io").value);
    const script = document.getElementById("script").value.trim();

    // Validação das entradas
    if (isNaN(cores) || cores < 1) {
      alert("A quantidade mínima de cores é 1.");
      event.preventDefault();
      return;
    }

    if (isNaN(memoria) || memoria < 0) {
      alert("A memória precisa ser maior que 0 MB.");
      event.preventDefault();
      return;
    }

    if (isNaN(io) || io <= 0) {
      alert("Informe um tempo de IO válido (maior que 0).");
      event.preventDefault();
      return;
    }

    if (script.length === 0) {
      alert("O campo de script não pode estar vazio.");
      event.preventDefault();
      return;
    }

    // Se tudo estiver válido, o formulário é enviado normalmente para o Flask
  });
});
