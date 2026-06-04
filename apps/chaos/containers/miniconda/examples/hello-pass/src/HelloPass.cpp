//===-- HelloPass.cpp - Example LLVM Pass (New Pass Manager) ----*- C++ -*-===//
//
// A demonstration pass that prints function statistics:
// - Function name
// - Number of basic blocks
// - Number of instructions
//
// Usage:
//   opt -load-pass-plugin ./HelloPass.so -passes=hello-pass -disable-output input.ll
//
//===----------------------------------------------------------------------===//

#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Plugins/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {

struct HelloPass : public PassInfoMixin<HelloPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
        unsigned numBB = 0;
        unsigned numInst = 0;

        for (BasicBlock &BB : F) {
            ++numBB;
            numInst += BB.size();
        }

        errs() << "=== HelloPass: " << F.getName() << " ===\n";
        errs() << "  Basic blocks:  " << numBB << "\n";
        errs() << "  Instructions:  " << numInst << "\n";
        errs() << "\n";

        return PreservedAnalyses::all();
    }

    // Required for the pass to be skipped when optnone is present
    static bool isRequired() { return true; }
};

} // anonymous namespace

//===----------------------------------------------------------------------===//
// Pass Plugin Registration (New Pass Manager)
//===----------------------------------------------------------------------===//

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION,
        "HelloPass",
        LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "hello-pass") {
                        FPM.addPass(HelloPass());
                        return true;
                    }
                    return false;
                });
        }
    };
}
