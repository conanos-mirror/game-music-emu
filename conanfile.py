from conans import ConanFile, tools, MSBuild
from conanos.build import config_scheme
import os, shutil


class GamemusicemuConan(ConanFile):
    name = "game-music-emu"
    version = "0.6.2"
    description = "Game_Music_Emu is a collection of video game music file emulators"
    url = "https://github.com/conanos/game-music-emu"
    homepage = "https://bitbucket.org/mpyne/game-music-emu/wiki/Home"
    license = "LGPL-v2.1+"
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        url_ = 'https://github.com/ShiftMediaProject/game-music-emu/archive/{version}.tar.gz'
        tools.get(url_.format(version=self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder,"SMP")):
                msbuild = MSBuild(self)
                build_type = str(self.settings.build_type) + ("DLL" if self.options.shared else "")
                msbuild.build("libgme.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'},build_type=build_type)

    def package(self):
        if self.settings.os == 'Windows':
            platforms={'x86': 'Win32', 'x86_64': 'x64'}
            rplatform = platforms.get(str(self.settings.arch))
            self.copy("*", dst=os.path.join(self.package_folder,"include"), src=os.path.join(self.build_folder,"..", "msvc","include"))
            if self.options.shared:
                for i in ["lib","bin"]:
                    self.copy("*", dst=os.path.join(self.package_folder,i), src=os.path.join(self.build_folder,"..","msvc",i,rplatform))
            self.copy("*", dst=os.path.join(self.package_folder,"licenses"), src=os.path.join(self.build_folder,"..", "msvc","licenses"))

            tools.mkdir(os.path.join(self.package_folder,"lib","pkgconfig"))
            shutil.copyfile(os.path.join(self.build_folder,self._source_subfolder,"gme","libgme.pc.in"),
                            os.path.join(self.package_folder,"lib","pkgconfig", "libgme.pc"))
            lib = "-lgmed" if self.options.shared else "-lgme"
            replacements = {
                "@CMAKE_INSTALL_PREFIX@"  :  self.package_folder,
                "@LIB_SUFFIX@"            :  "",
                "@GME_VERSION@"           :  self.version,
                "-lgme"                   :  lib
            }
            for s, r in replacements.items():
                tools.replace_in_file(os.path.join(self.package_folder,"lib","pkgconfig", "libgme.pc"),s,r)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

