const hre = require("hardhat");

async function main() {
  console.log("🛡️ Deploying Sentinels of Integrity contracts...\n");

  // Deploy IntegrityHash
  const IntegrityHash = await hre.ethers.getContractFactory("IntegrityHash");
  const integrityHash = await IntegrityHash.deploy();
  await integrityHash.waitForDeployment();
  console.log(`✅ IntegrityHash deployed to: ${await integrityHash.getAddress()}`);

  // Deploy ContentRegistry
  const ContentRegistry = await hre.ethers.getContractFactory("ContentRegistry");
  const contentRegistry = await ContentRegistry.deploy();
  await contentRegistry.waitForDeployment();
  console.log(`✅ ContentRegistry deployed to: ${await contentRegistry.getAddress()}`);

  // Deploy ZKVerifier
  const ZKVerifier = await hre.ethers.getContractFactory("ZKVerifier");
  const zkVerifier = await ZKVerifier.deploy();
  await zkVerifier.waitForDeployment();
  console.log(`✅ ZKVerifier deployed to: ${await zkVerifier.getAddress()}`);

  // Deploy MerkleProof
  const MerkleProof = await hre.ethers.getContractFactory("MerkleProof");
  const merkleProof = await MerkleProof.deploy();
  await merkleProof.waitForDeployment();
  console.log(`✅ MerkleProof deployed to: ${await merkleProof.getAddress()}`);

  // Deploy MultiSigValidator (requires 5 validator addresses)
  const signers = await hre.ethers.getSigners();
  if (signers.length >= 5) {
    const validators = signers.slice(0, 5).map(s => s.address);
    const MultiSig = await hre.ethers.getContractFactory("MultiSigValidator");
    const multiSig = await MultiSig.deploy(validators);
    await multiSig.waitForDeployment();
    console.log(`✅ MultiSigValidator deployed to: ${await multiSig.getAddress()}`);
  } else {
    console.log("⚠️  MultiSigValidator skipped — need 5 signers");
  }

  console.log("\n🎉 All contracts deployed successfully!");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
