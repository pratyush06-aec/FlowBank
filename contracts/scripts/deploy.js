import hre from "hardhat";

async function main() {
  console.log("Starting deployment...");

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contract with account:", deployer.address);

  const BankOSAccount = await hre.ethers.getContractFactory("BankOSAccount");
  const bankAccount = await BankOSAccount.deploy(deployer.address, deployer.address);

  await bankAccount.waitForDeployment();
  
  const address = await bankAccount.getAddress();
  console.log("BankOSAccount deployed to:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
