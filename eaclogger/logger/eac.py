import time
import hashlib
import whipper
from whipper.common import common
from whipper.result import result


class EacLogger(result.Logger):

    _accuratelyRipped = 0
    _inARDatabase = 0
    _errors = False

    # Overrides whipper's common implementation because EAC writes minutes
    # value without zero padding it (EAC: %2d) vs (whipper: %02d)
    def _framesToMSF(self, frames):
        """Returns MSF representation of the provided frames value"""

        f = frames % common.FRAMES_PER_SECOND
        frames -= f
        s = (frames / common.FRAMES_PER_SECOND) % 60
        frames -= s * 60
        m = frames / common.FRAMES_PER_SECOND / 60
        return "%2d:%02d.%02d" % (m, s, f)

    # Overrides whipper's common implementation because EAC writes hours
    # value without zero padding it (EAC: %2d) vs (whipper: %02d)
    # HMSF is used to represent pre-gaps' duration
    def _framesToHMSF(self, frames):
        """Returns HMSF representation of the provided frames value"""

        f = frames % common.FRAMES_PER_SECOND
        frames -= f
        s = (frames / common.FRAMES_PER_SECOND) % 60
        frames -= s * 60
        m = frames / common.FRAMES_PER_SECOND / 60
        frames -= m * 60
        h = frames / common.FRAMES_PER_SECOND / 60 / 60
        return "%2d:%02d:%02d.%02d" % (h, m, s, f)

    def log(self, ripResult, epoch=time.time()):
        """Returns big str: logfile joined text lines"""

        lines = self.logRip(ripResult, epoch=epoch)
        return "\n".join(lines)

    def logRip(self, ripResult, epoch):
        """Returns lines list"""

        lines = []

        # Ripper version
        # ATM differs from EAC's typical log line
        lines.append("whipper version %s (eac logger)" % whipper.__version__)
        lines.append("")

        # Rip date
        # ATM differs from EAC's typical log line
        date = time.strftime("%d. %B %Y, %R", time.gmtime(epoch)).strip()
        lines.append("whipper extraction logfile from %s" % date)
        lines.append("")

        # Artist / Album
        lines.append("%s / %s" % (ripResult.artist, ripResult.title))
        lines.append("")

        # Drive information
        # Missing information about "Adapter" (not relevant on *nix?)
        lines.append(
            "Used drive  : %s%s" % (
                ripResult.vendor, ripResult.model))
        lines.append("")

        # Rip settings
        lines.append("Read mode               : Secure")
        # Extra line (not included in EAC's logfiles)
        lines.append("Use cdparanoia mode     : Yes (cdparanoia %s)" % (
            ripResult.cdparanoiaVersion))
        defeat = "Unknown"
        if ripResult.cdparanoiaDefeatsCache is True:
            defeat = "Yes"
        if ripResult.cdparanoiaDefeatsCache is False:
            defeat = "No"
        lines.append("Defeat audio cache      : %s" % defeat)
        lines.append("Make use of C2 pointers : No")
        lines.append("")
        lines.append("Read offset correction                      : %d" %
                     ripResult.offset)
        # Currently unsupported by unpatched cdparanoia
        lines.append("Overread into Lead-In and Lead-Out          : No")
        lines.append("Fill up missing offset samples with silence : Yes")
        lines.append("Delete leading and trailing silent blocks   : No")
        lines.append("Null samples used in CRC calculations       : Yes")
        # Missing line "Used interface" (not relevant on *nix?)
        # Extra line (not included in EAC's logfiles)
        lines.append("Gap detection                               : "
                     "cdrdao version %s" % ripResult.cdrdaoVersion)
        lines.append("Gap handling                                : "
                     "Appended to previous track")
        lines.append("")

        # Missing lines (unneeded?): "Selected bitrate", "Quality"
        lines.append("Used output format              : FLAC")
        lines.append("Add ID3 tag                     : No")
        # Handle the case in which the distutils module isn't available
        try:
            from distutils.spawn import find_executable
            flacPath = find_executable("flac")
        except ImportError:
            flacPath = "Unknown"
        lines.append("Command line compressor         : %s" % flacPath)
        lines.append("Additional command line options : "
                     "--silent --verify -o %%d -f %%s")
        lines.append("")
        lines.append("")

        # TOC
        lines.append("TOC of the extracted CD")
        lines.append("")
        lines.append(
            "     Track |   Start  |  Length  | Start sector | End sector ")
        lines.append(
            "    ---------------------------------------------------------")
        table = ripResult.table

        htoa = None
        try:
            htoa = table.tracks[0].getIndex(0)
        except KeyError:
            pass

        # If true include HTOA line in log's TOC
        if htoa and htoa.path:
            htoastart = htoa.absolute
            htoaend = table.getTrackEnd(0)
            htoalength = table.tracks[0].getIndex(1).absolute - htoastart
            lines.append(
                "       %2d  | %s | %s |    %6d    |   %6d   " % (
                    0,
                    self._framesToMSF(htoastart),
                    self._framesToMSF(htoalength),
                    htoastart, htoaend))

        # For every track include information in the TOC
        for t in table.tracks:
            start = t.getIndex(1).absolute
            length = table.getTrackLength(t.number)
            end = table.getTrackEnd(t.number)
            lines.append(
                "       %2d  | %s | %s |    %6d    |   %6d   " % (
                    t.number,
                    self._framesToMSF(start),
                    self._framesToMSF(length),
                    start, end))
        lines.append("")
        lines.append("")

        # per-track
        for t in ripResult.tracks:
            if not t.filename:
                continue
            track_lines, ARDB_entry, ARDB_match = self.trackLog(t)
            self._inARDatabase += int(ARDB_entry)
            self._accuratelyRipped += int(ARDB_match)
            lines.extend(track_lines)
            lines.append("")

        # AccurateRip summary at the end of the logfile
        if self._inARDatabase == 0:
            lines.append("None of the tracks are present "
                         "in the AccurateRip database")
        else:
            nonHTOA = len(ripResult.tracks)
            if ripResult.tracks[0].number == 0:
                nonHTOA -= 1
            if self._accuratelyRipped == 0:
                lines.append("No tracks could be verified as accurate")
                lines.append(
                    "You may have a different pressing "
                    "from the one(s) in the database")
            elif self._accuratelyRipped < nonHTOA:
                lines.append("%d track(s) accurately ripped" %
                             self._accuratelyRipped)
                lines.append("%d track(s) could not be verified as accurate" %
                             (nonHTOA - self._accuratelyRipped))
                lines.append("")
                lines.append("Some tracks could not be verified as accurate")

            else:
                lines.append("All tracks accurately ripped")
        lines.append("")

        # FIXME: ATM this will always pick else
        # When does EAC report errors? (only on abort?)
        if self._errors:
            lines.append("There were errors")
        else:
            lines.append("No errors occurred")
        lines.append("")

        # END of ripper status report
        # in EAC this isn't always the second to last line in the log because
        # plugins information are included beneath (but before log checksum)
        lines.append("End of status report")
        lines.append("")

        # Log checksum (uppercase hex encoded SHA256 hash of all lines)
        # It isn't compatible with EAC's one: checklog fail
        hasher = hashlib.sha256()
        hasher.update("\n".join(lines).encode("utf-8"))
        lines.append("==== Log checksum %s ====" % hasher.hexdigest().upper())
        lines.append("")

        return lines

    def trackLog(self, trackResult):
        """Returns tracks section lines: data picked from trackResult"""

        lines = []

        # Track number (formatting like EAC's one)
        if trackResult.number < 10:
            lines.append("Track  %2d" % trackResult.number)
        else:
            lines.append("Track %2d" % trackResult.number)
        lines.append("")

        # Filename (including path) of ripped track
        lines.append("     Filename %s" % trackResult.filename)
        lines.append("")

        # Pre-gap length
        # EAC always adds 2 seconds to the first track pre-gap
        pregap = trackResult.pregap
        if trackResult.number == 1:
            pregap += 2 * common.FRAMES_PER_SECOND
        if pregap:
            lines.append("     Pre-gap length  %s" % self._framesToHMSF(
                pregap))
            lines.append("")

        # Peak level
        # EAC seems to format peak differently, truncating to the 3rd digit,
        # and also calculating it against a max of 32767
        # MBV - Feed me with your kiss: replaygain 0.809875,
        # EAC's peak level 80.9 % instead of 90.0 %
        peak = trackResult.peak * 32768 / 32767
        lines.append("     Peak level %.1f %%" % (
            int(peak * 1000) / 10.0))

        # Extraction speed
        if trackResult.copyspeed:
            lines.append("     Extraction speed %.1f X" % (
                trackResult.copyspeed))

        # Track quality
        if trackResult.quality and trackResult.quality > 0.001:
            lines.append("     Track quality %.1f %%" % (
                trackResult.quality * 100.0, ))

        # Ripper test CRC
        if trackResult.testcrc is not None:
            lines.append("     Test CRC %08X" % trackResult.testcrc)

        # Ripper copy CRC
        if trackResult.copycrc is not None:
            lines.append("     Copy CRC %08X" % trackResult.copycrc)

        # AccurateRip track status
        # No support for AccurateRip v2 before whipper 0.5.1
        ARDB_entry = 0
        ARDB_match = 0
        if trackResult.AR["v2"]["DBCRC"]:
            ARDB_entry += 1
            if trackResult.AR["v2"]["CRC"] == trackResult.AR["v2"]["DBCRC"]:
                lines.append("     Accurately ripped "
                             "(confidence %d)  [%s]  (AR v2)" % (
                              trackResult.AR["v2"]["DBConfidence"],
                              trackResult.AR["v2"]["DBCRC"].upper())
                             )
                ARDB_match += 1
        elif trackResult.AR["v1"]["DBCRC"]:
            ARDB_entry += 2
            if trackResult.AR["v1"]["CRC"] == trackResult.AR["v1"]["DBCRC"]:
                lines.append("     Accurately ripped "
                             "(confidence %d)  [%s]  (AR v1)" % (
                              trackResult.AR["v1"]["DBConfidence"],
                              trackResult.AR["v1"]["DBCRC"].upper())
                             )
                ARDB_match += 1
        else:
            lines.append("     Track not present in AccurateRip database")
        if ARDB_entry == 1 and ARDB_match == 0:
            lines.append("     Cannot be verified as accurate  "
                         "(confidence %d)  [%s], AccurateRip "
                         "returned [%s]  (AR v2)" % (
                          trackResult.AR["v2"]["DBConfidence"],
                          trackResult.AR["v2"]["CRC"].upper(),
                          trackResult.AR["v2"]["DBCRC"].upper())
                         )
        elif ARDB_entry == 2 and ARDB_match == 0:
            lines.append("     Cannot be verified as accurate  "
                         "(confidence %d)  [%s], AccurateRip "
                         "returned [%s]  (AR v1)" % (
                          trackResult.AR["v1"]["DBConfidence"],
                          trackResult.AR["v1"]["CRC"].upper(),
                          trackResult.AR["v1"]["DBCRC"].upper())
                         )

        # EAC emits zero warnings even when a CRC mismatch occurs
        if trackResult.testcrc == trackResult.copycrc:
            lines.append("     Copy OK")
        return lines, bool(ARDB_entry), bool(ARDB_match)
