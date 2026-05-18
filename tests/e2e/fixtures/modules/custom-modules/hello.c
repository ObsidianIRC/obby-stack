#include "unrealircd.h"

ModuleHeader MOD_HEADER = {
	"third/hello",
	"1.0",
	"e2e autoload fixture",
	"ObbyIRCd",
	"unrealircd-6",
};

MOD_TEST() { return MOD_SUCCESS; }
MOD_INIT() { MARK_AS_OFFICIAL_MODULE(modinfo); return MOD_SUCCESS; }
MOD_LOAD() { return MOD_SUCCESS; }
MOD_UNLOAD() { return MOD_SUCCESS; }
