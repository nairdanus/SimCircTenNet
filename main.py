from . train import train


train(dataset="10_animals_plants",
      syntax="bow",
      ansatz="iqp",
      layers=2,
      q_s=1,
      q_n=1,
      q_pp=1,
      𝓧=None,
      fidelity=100,
      )