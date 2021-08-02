
f2py3 --overwrite-signature -m _wdm_lib -h wdm.pyf \
                   DTTM90.f TSBUFR.f UTCHAR.f UTCP90.f UTDATE.f UTNUMB.f \
                   UTWDMD.f UTWDMF.f UTWDT1.f WDATM1.f WDATM2.f WDATRB.f \
                   WDBTCH.f WDMESS.f WDMID.f WDOP.f WDTMS1.f WDTMS2.f    \
                   only: \
                   timcvt timdif wdbopn wdbsac wdbsai wdbsar wdbsgc wdbsgi \
                   wdbsgr wdckdt wdflcl wdlbax wdtget wdtput wtfndt wddsrn \
                   wddsdl wddscl

## Need to tell f2py which subroutine arguments are actually output.
#sed -i -e 's/integer :: retcod/integer intent(out) :: retcod/g' \
#       -e 's/integer :: psa/integer intent(out) :: psa/g' \
#       -e 's/integer, optional,check(len(saval)>=salen),depend(saval) :: salen=len(saval)/integer depend(saval) :: salen/g' \
#       -e 's/integer :: tdsfrc/integer intent(out) :: tdsfrc/g' \
#       -e 's/integer dimension(6) :: sdat/integer intent(out), dimension(6) :: sdat/g' \
#       -e 's/integer dimension(6) :: edat/integer intent(out), dimension(6) :: edat/g' \
#       -e 's/integer :: nvals/integer intent(out) :: nvals/g' \
#       -e 's/real dimension(nval) :: rval/real intent(out), dimension(nval), depend(nval) :: rval/g' \
#       -e 's/integer depend(saval) :: salen/integer intent(in) :: salen/g' \
#       -e 's/dimension(salen) :: saval/intent(in), dimension(salen) :: saval/g' \
#       wdm.pyf
