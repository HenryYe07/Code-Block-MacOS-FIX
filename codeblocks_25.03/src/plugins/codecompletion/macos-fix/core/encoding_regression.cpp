#include <wx/init.h>
#include <wx/string.h>
#include <wx/file.h>
#include <configmanager.h>
#include <manager.h>
#include <encodingdetector.h>
#include <cstdio>
#include <vector>
class TestConfig : public ConfigManager {
public: using ConfigManager::SetUserDataFolder;
};
int failures = 0;
void check(const char* name, const std::vector<wxByte>& bytes, const wxString& expected,
           bool expectedOK = true) {
    const wxByte empty = 0;
    EncodingDetector result(bytes.empty() ? &empty : bytes.data(), bytes.size(), false);
    const bool pass = result.IsOK() == expectedOK && (!expectedOK || result.GetWxStr() == expected);
    std::printf("%s: %s (encoding=%d, characters=%zu)\n",name,pass ? "PASS" : "FAIL",
                (int)result.GetFontEncoding(),result.GetWxStr().length());
    if (!pass) ++failures;
}
int main() {
    wxInitializer init;
    if (!init.IsOk()) return 2;
    TestConfig::SetUserDataFolder("/private/tmp/codeblocks-encoding-regression-config");
    ConfigManager* config = Manager::Get()->GetConfigManager("editor");
    config->Write("/default_encoding/use_option", 0);
    config->Write("/default_encoding/use_system", false);
    check("UTF-8 Chinese", {0xe4,0xb8,0xad,0xe6,0x96,0x87}, wxString::FromUTF8("中文"));
    check("UTF-8 BOM", {0xef,0xbb,0xbf,'A'}, "A");
    check("UTF-16 LE", {0xff,0xfe,0x2d,0x4e,0x87,0x65,0x0a,0x00}, wxString::FromUTF8("中文\n"));
    check("UTF-16 BE", {0xfe,0xff,0x4e,0x2d,0x65,0x87,0x00,0x0a}, wxString::FromUTF8("中文\n"));
    check("UTF-32 LE", {0xff,0xfe,0,0,0x2d,0x4e,0,0}, wxString::FromUTF8("中"));
    check("UTF-32 BE", {0,0,0xfe,0xff,0,0,0x4e,0x2d}, wxString::FromUTF8("中"));
    check("BOM only", {0xef,0xbb,0xbf}, "");
    check("Empty buffer", {}, "");
    config->Write("/default_encoding/use_option", 1);
    config->Write("/default_encoding", "UTF-8");
    check("ASCII", {'i','n','t',' ','x',';'}, "int x;");
    const wchar_t embedded[] = {L'A',0,L'B'};
    check("Embedded NUL", {'A',0,'B'}, wxString(embedded,3));
    check("Malformed UTF-8", {0xc3,0x28}, "", false);
    config->Write("/default_encoding", "WINDOWS-1252");
    check("Legacy CP1252", {'c','a','f',0xe9}, wxString::FromUTF8("café"));
    config->Write("/default_encoding", "GB2312");
    check("Legacy Chinese", {0xd6,0xd0,0xce,0xc4}, wxString::FromUTF8("中文"));
    config->Write("/default_encoding/use_option", 0);
    config->Write("/default_encoding/use_system", true);
    check("System encoding ASCII", {'i','n','t',' ','x',';'}, "int x;");
    wxFile file("/private/tmp/codeblocks-empty-encoding-test.cpp", wxFile::write);
    file.Close();
    EncodingDetector emptyFile("/private/tmp/codeblocks-empty-encoding-test.cpp",false);
    if (!emptyFile.IsOK() || !emptyFile.GetWxStr().empty()) ++failures;
    std::printf("Empty file: %s\n",emptyFile.IsOK() ? "PASS" : "FAIL");
    return failures ? 1 : 0;
}
