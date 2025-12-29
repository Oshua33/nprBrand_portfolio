module.exports = {
  apps: [{
    name: "olusolaBackend",
    script: "python3 -m nprOlusolaBe.serve",
    env: {
      DEBUG: false

    }
  }]
}
