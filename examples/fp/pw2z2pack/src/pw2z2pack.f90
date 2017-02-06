!
! Copyright (C) 2003-2013 Quantum ESPRESSO and Wannier90 groups
! This file is distributed under the terms of the
! GNU General Public License. See the file `License'
! in the root directory of the present distribution,
! or http://www.gnu.org/copyleft/gpl.txt .
!
! pw2z2pack - G. Autes - gabriel.autes@epfl.ch
!  compute the overlap matrix required by z2Pack
!  and write then in seedname.mmn file
! to be implemented:
!  collinear case 
!  parallelization
!
! based on:
!   -pw2wannier written by Stefano de Gironcoli
!    with later additions by
!    Jonathan Yates - spinors
!   -sym_band.f90 for the symmetry part
!
! uspp implementation has to be checked
!
module z2pack
   USE kinds, only : DP
   !integer, allocatable :: nnb(:)       ! #b  (ik)
   integer              :: nnb          ! #b
   integer, allocatable :: kpb(:,:)     ! k+b (ik,ib)
   integer, allocatable :: g_kpb(:,:,:) ! G_k+b (ipol,ik,ib)
   integer, allocatable :: ig_(:,:)     ! G_k+b (ipol,ik,ib)
   logical, allocatable :: excluded_band(:)
   integer  :: n_wannier !number of WF
   integer               :: ispinw, ikstart, ikstop, iknum
   CHARACTER(len=256) :: seedname  = 'wannier'  ! prepended to file names in wannier90
   ! For implementation of wannier_lib
   real(DP)              :: rlatt(3,3),glatt(3,3) ! real and recip lattices (Cartesian co-ords, units of Angstrom)
   real(DP), allocatable :: kpt_latt(:,:)  ! k-points in crystal co-ords. kpt_latt(3,iknum)  
   real(DP), allocatable :: atcart(:,:)    ! atom centres in Cartesian co-ords and Angstrom units. atcart(3,nat)
   integer               :: num_bands      ! number of bands left after exclusions
   character(len=3), allocatable :: atsym(:) ! atomic symbols. atsym(nat)
   integer               :: num_nnmax=12
   complex(DP), allocatable :: m_mat(:,:,:,:)
   integer               :: isym     ! symmetry (see header of pw.x calculation with verbosity = 'high'
                                     ! to find the isym corresponding to the required symmetry
   complex(DP)           :: sym_eig  ! symmetry eigenvalue of the subspace on which the states are projected 
   integer               :: iun_mmn,iun_i,iun_mi
   integer               :: nexband  ! number of lower excluded bands 
   integer               :: nexsym   ! number of bands excluded by symmetry 
   logical, allocatable  :: excluded_sym(:)
   logical               :: tr       ! time reversal symmetry
   real(DP)              :: sym_thr,deg_thr ! threshold for the symmetry eigenvalue and the band degeneracy
end module z2pack
!


!------------------------------------------------------------------------
PROGRAM pw2z2pack
  ! This is the interface to the Wannier90 code: see http://www.wannier.org
  !------------------------------------------------------------------------
  !
  USE io_global,  ONLY : stdout, ionode, ionode_id
  USE mp_global,  ONLY : mp_startup
  USE mp,         ONLY : mp_bcast
  USE mp_world,   ONLY : world_comm
  USE cell_base,  ONLY : at, bg
  USE lsda_mod,   ONLY : nspin, isk
  USE klist,      ONLY : nkstot,xk
  USE io_files,   ONLY : prefix, tmp_dir
  USE noncollin_module, ONLY : noncolin
  USE control_flags,    ONLY : gamma_only
  USE environment,ONLY : environment_start,environment_end
  USE wvfct,      ONLY : nbnd,ecutwfc
  USE gvect,     ONLY : g, gg
  USE constants, ONLY : eps6
  USE z2pack
  !
  IMPLICIT NONE
  !
  CHARACTER(LEN=256), EXTERNAL :: trimcheck
  !
  INTEGER :: ios,ik,ig,ib,i1,i2,i3,gmin(3),sg
  REAL(DP) :: g_(3), gg_,k_(3),kp_(3),dmin
  CHARACTER(len=4) :: spin_component
  CHARACTER(len=256) :: outdir

  ! these are in wannier module.....-> integer :: ispinw, ikstart, ikstop, iknum
  NAMELIST / inputpp / outdir, prefix, spin_component,  &
       seedname, isym,nexband ,sym_eig,tr,sym_thr,deg_thr
  !
  ! initialise environment
  !
#ifdef __MPI
  CALL mp_startup ( )
#endif
  CALL environment_start ( 'PW2Z2PACK' )
  !
  ! Read input on i/o node and broadcast to the rest
  !
  ios = 0
  IF(ionode) THEN
     !
     ! Check to see if we are reading from a file
     !
     CALL input_from_file()
     !
     !   set default values for variables in namelist
     !
     CALL get_environment_variable( 'ESPRESSO_TMPDIR', outdir )
     IF ( trim( outdir ) == ' ' ) outdir = './'
     prefix   = ' '
     seedname = 'wannier'
     spin_component = 'none'
     isym     = 0
     nexband  = 0
     sym_eig = 1.0d0
     tr=.false.
     sym_thr=1d-3
     deg_thr=eps6
     !
     !     reading the namelist inputpp
     !
     READ (5, inputpp, iostat=ios)
     !
     !     Check of namelist variables
     !
     tmp_dir = trimcheck(outdir)
     ! back to all nodes
  ENDIF
  !
  CALL mp_bcast(ios,ionode_id, world_comm)
  IF (ios /= 0) CALL errore( 'pw2z2pack', 'reading inputpp namelist', abs(ios))
  !
  ! broadcast input variable to all nodes
  !
  CALL mp_bcast(outdir,ionode_id, world_comm)
  CALL mp_bcast(tmp_dir,ionode_id, world_comm)
  CALL mp_bcast(prefix,ionode_id, world_comm)
  CALL mp_bcast(seedname,ionode_id, world_comm)
  CALL mp_bcast(spin_component,ionode_id, world_comm)
  CALL mp_bcast(isym,ionode_id, world_comm)
  CALL mp_bcast(nexband,ionode_id, world_comm)
  !
  !   Now allocate space for pwscf variables, read and check them.
  !
  !logwann = .true.
  WRITE(stdout,*)
  WRITE(stdout,*) ' Reading nscf_save data'
  CALL read_file
  WRITE(stdout,*)
  !
! check we are in the non-collinear case
  IF(.not.noncolin) CALL errore('pw2z2pack','Only works for non-collinear case ',1)
  IF (noncolin.and.gamma_only) CALL errore('pw2z2pack',&
       'Non-collinear and gamma_only not implemented',1)

  !
  SELECT CASE ( trim( spin_component ) )
  CASE ( 'up' )
     WRITE(stdout,*) ' Spin CASE ( up )'
     ispinw  = 1
     ikstart = 1
     ikstop  = nkstot/2
     iknum   = nkstot/2
  CASE ( 'down' )
     WRITE(stdout,*) ' Spin CASE ( down )'
     ispinw = 2
     ikstart = nkstot/2 + 1
     ikstop  = nkstot
     iknum   = nkstot/2
  CASE DEFAULT
     IF(noncolin) THEN
        WRITE(stdout,*) ' Spin CASE ( non-collinear )'
     ELSE
        WRITE(stdout,*) ' Spin CASE ( default = unpolarized )'
     ENDIF
     ispinw = 0
     ikstart = 1
     ikstop  = nkstot
     iknum   = nkstot
  END SELECT
  !
  !
  !
  WRITE(stdout,*) ' -----------------'
  WRITE(stdout,*) ' *** Building nnkp '
  WRITE(stdout,*) ' -----------------'
  WRITE(stdout,*)
!  CALL read_nnkp
!  here build nkb instead, assuming all k-points are aligned along the string 
!  nnb=2
!  allocate(kpb(iknum,nnb))     ! k+b (ik,ib)
!  allocate(g_kpb(3,iknum,nnb))     ! k+b (ik,ib)
!  do ik=1,iknum
!    kpb(ik,1)=ik-1
!    kpb(ik,2)=ik+1
!    if(ik==1) kpb(ik,1)=iknum
!    if(ik==iknum) kpb(ik,2)=1
!  enddo
! here: only the neighbors required by z2pack
  nnb=1
  allocate(kpb(iknum,nnb))     ! k+b (ik,ib)
  allocate(g_kpb(3,iknum,nnb))     ! k+b (ik,ib)
  do ik=1,iknum
    kpb(ik,1)=ik+1
!    kpb(ik,2)=ik+1
    if(ik==iknum) kpb(ik,1)=1
!    if(ik==iknum) kpb(ik,2)=1
  enddo


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  g_kpb(:,:,:)=0
  if(ionode) write(stdout,'(a)') '   ik  ikp    g_kpb'
!  do ik=1,iknum  
!    do ib=1,nnb
!     dmin=100.0d0
!     do i1=-1,1
!     do i2=-1,1
!     do i3=-1,1
!         k_ =xk(:,ik)
!         kp_=xk(:,kpb(ik,ib))
!         g_(1) = REAL(i1)  
!         g_(2) = REAL(i2)  
!         g_(3) = REAL(i3)  
!         call cryst_to_cart(1, g_ , bg , 1)
!         g_ =kp_+g_-k_ 
!         gg_= g_(1)*g_(1) + g_(2)*g_(2) + g_(3)*g_(3)
!         if(gg_.lt.dmin)then
!           dmin=gg_
!           gmin(1)=i1      
!           gmin(2)=i2      
!           gmin(3)=i3      
!         endif
!     enddo
!     enddo
!     enddo      
!     g_kpb(:,ik,ib)=gmin
     k_ =xk(:,iknum)
     kp_=xk(:,kpb(iknum,1))
!     write(*,*) k_
!     write(*,*) kp_
     call cryst_to_cart(1, k_  , at , -1)
     call cryst_to_cart(1, kp_ , at , -1)
!     write(*,*) k_
!     write(*,*) kp_
!     sg=-1
!     if(k_(1)>=kp_(1)) sg=1
!     g_kpb(1,iknum,1)=sg*nint(abs(k_(1)-kp_(1))   )  
!     sg=-1
!     if(k_(2)>=kp_(2)) sg=1
!     g_kpb(2,iknum,1)=sg*nint(abs(k_(2)-kp_(2))   )  
!     sg=-1
!     if(k_(3)>=kp_(3)) sg=1
!     g_kpb(3,iknum,1)=sg*nint(abs(k_(3)-kp_(3))   )  
!
  g_kpb(1,iknum,1)=nint(k_(1)-kp_(1))     
  g_kpb(2,iknum,1)=nint(k_(2)-kp_(2))     
  g_kpb(3,iknum,1)=nint(k_(3)-kp_(3))     

  do ik=1,iknum  
    do ib=1,nnb
     if(ionode)then
      write(stdout,'(5i5)') ik,kpb(ik,ib),g_kpb(:,ik,ib)
     endif
    enddo
  enddo
  if(ionode) write(stdout,*) 
  

!!! to be checked
  ALLOCATE( ig_(iknum,nnb)) !, ig_check(iknum,nnb) )
!!!
  DO ik=1, iknum
     DO ib = 1, nnb
        g_(:) = REAL( g_kpb(:,ik,ib) )
        CALL cryst_to_cart (1, g_, bg, 1)
        gg_ = g_(1)*g_(1) + g_(2)*g_(2) + g_(3)*g_(3)
        ig_(ik,ib) = 0
        ig = 1
        DO WHILE  (gg(ig) <= gg_ + eps6)
           IF ( (abs(g(1,ig)-g_(1)) < eps6) .and.  &
                (abs(g(2,ig)-g_(2)) < eps6) .and.  &
                (abs(g(3,ig)-g_(3)) < eps6)  ) ig_(ik,ib) = ig
           ig= ig +1
        ENDDO
     ENDDO
  ENDDO
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

! take care of excluded bands 
! WARNING: can only exclude lower bands
  allocate(excluded_band(nbnd))
  allocate(excluded_sym(nbnd))
  excluded_band=.false.
  excluded_sym =.false.
  if(nexband>0)  excluded_band(1:nexband)=.true.
  num_bands=nbnd-nexband
  nexsym=0
  if(isym>0) nexsym=num_bands/2
  
  if(ionode) write(stdout,'( "   lower bands excluded      ", i5)')  nexband
  if(ionode) write(stdout,'( "   bands excluded by symmetry", i5)')  nexsym
  if(ionode) write(stdout,'( "   overlap matrix size       ", i5)')  num_bands-nexsym
  if(ionode) write(stdout,*)
  if(ionode) write(stdout,*)

  CALL mp_bcast(nnb,ionode_id, world_comm)
  CALL mp_bcast(kpb,ionode_id, world_comm)
  CALL mp_bcast(g_kpb,ionode_id, world_comm)
  CALL mp_bcast(num_bands,ionode_id, world_comm)
  CALL mp_bcast(excluded_band,ionode_id, world_comm)
  CALL mp_bcast(excluded_sym,ionode_id, world_comm)
  CALL mp_bcast(nexband,ionode_id, world_comm)
  CALL mp_bcast(nexsym,ionode_id, world_comm)


 WRITE(stdout,*) ' Opening pp-files '
  CALL openfil_pp
  WRITE(stdout,*)
  WRITE(stdout,*)
  WRITE(stdout,*) ' ---------------'
  WRITE(stdout,*) ' *** Compute  M '
  WRITE(stdout,*) ' ---------------'
  WRITE(stdout,*)
  CALL compute_mmn
  WRITE(stdout,*)
  WRITE(stdout,*) ' ------------'
  WRITE(stdout,*) ' *** Stop pp '
  WRITE(stdout,*) ' ------------'
  WRITE(stdout,*)
  !
  CALL environment_end ( 'PW2Z2PACK' )
  IF ( ionode ) WRITE( stdout, *  )
  CALL stop_pp
  STOP
END PROGRAM pw2z2pack
!-----------------------------------------------------------------------
SUBROUTINE compute_mmn
   !-----------------------------------------------------------------------
   !
   USE io_global,  ONLY : stdout, ionode
   USE kinds,           ONLY: DP
   USE wvfct,           ONLY : nbnd, npw, npwx, igk, g2kin
   USE control_flags,   ONLY : gamma_only
   USE wavefunctions_module, ONLY :  psic, psic_nc
   USE fft_base,        ONLY : dffts, dfftp
   USE fft_interfaces,  ONLY : fwfft, invfft
   USE gvecs,         ONLY : nls, nlsm 
   USE klist,           ONLY : nkstot, xk
   USE io_files,        ONLY : nwordwfc, iunwfc
   USE gvect,           ONLY : g, ngm, gstart, nl
   USE cell_base,       ONLY : tpiba2, omega, alat, tpiba, at, bg
   USE ions_base,       ONLY : nat, ntyp => nsp, ityp, tau
   USE constants,       ONLY : tpi
!!!!!!!!!!!!!!!!!!!!!!! USPP NC !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!   USE uspp,            ONLY : nkb, vkb
   USE uspp,            ONLY : nkb, vkb, indv, nhtol,nhtoj
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   USE uspp_param,      ONLY : upf, nh, lmaxq
   USE becmod,          ONLY : bec_type, becp, calbec, &
                               allocate_bec_type, deallocate_bec_type
   USE mp_global,       ONLY : intra_pool_comm
   USE mp,              ONLY : mp_sum
   USE noncollin_module,ONLY : noncolin, npol
   USE wvfct,           ONLY : ecutwfc
   USE symm_base,       ONLY : ftau
   USE z2pack
!!!!!!!!!!!!!!!!!!!!!!! USPP NC !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   USE spin_orb,        ONLY : lspinorb, fcoef
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


   IMPLICIT NONE
   !
   INTEGER, EXTERNAL :: find_free_unit
   !
   complex(DP), parameter :: cmplx_i=(0.0_DP,1.0_DP)
   !
   INTEGER :: mmn_tot, ik, ikp, ipol, ib, npwq, i, m, n
   INTEGER :: ikb, jkb, ih, jh, na, nt, ijkb0, ind, nbt
   INTEGER :: ikevc, ikpevcq, s, counter, iktot, jk, jkp
   COMPLEX(DP), ALLOCATABLE :: phase(:), aux(:), aux2(:),evc(:,:),&
                               evcq(:,:),evck(:,:,:), &
                               becp2(:,:), Mkb(:,:), aux_nc(:,:) 
   real(DP), ALLOCATABLE    :: rbecp2(:,:)
   COMPLEX(DP), ALLOCATABLE :: qb(:,:,:,:), qgm(:)
   real(DP), ALLOCATABLE    :: qg(:), ylm(:,:), dxk(:,:)
   INTEGER, ALLOCATABLE     :: igkq(:)
   COMPLEX(DP)              :: mmn, zdotc, phase1
   real(DP)                 :: arg, g_(3)
   CHARACTER (len=9)        :: cdate,ctime
   CHARACTER (len=60)       :: header
   LOGICAL                  :: any_uspp
   INTEGER                  :: nn,inn,loop,loop2
   LOGICAL                  :: nn_found
   INTEGER                  :: istart,iend
   INTEGER                  :: ibnd_n, ibnd_m
   LOGICAL                  :: non_symmorphic
   INTEGER                  :: ftau_(3)
   logical, allocatable     :: excluded_symb(:)
   logical, allocatable     :: excluded_syma(:)

!!!!!!!!!!!!!!!!!!!!!!! USPP NC !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   INTEGER :: is1,is2,kh,iun_mmn_nouspp
   COMPLEX(DP), ALLOCATABLE :: becp2_nc(:,:,:), be1(:,:),be2(:,:), &
                               Mkb_nouspp(:,:) !! for testing only
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

   CALL start_clock( 'compute_mmn' )

   any_uspp = any(upf(1:ntyp)%tvanp)

!!!!!!!!!!!!!!!!!!!! USPP NC !!!!!!!!!!!!!!!!!!!!!
   IF(any_uspp .and. isym.ne.0) CALL errore('pw2z2pack',&
       'lsym =/=0 not implemented with USP',1)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

   ALLOCATE( phase(dffts%nnr), igkq(npwx) )
   ALLOCATE( evcq(npol*npwx,nbnd) )
   ALLOCATE( evc(npol*npwx,nbnd) )
   ALLOCATE( evck(npol*npwx,nbnd,iknum) )
   ALLOCATE( excluded_symb(nbnd) )
   ALLOCATE( excluded_syma(nbnd) )

   IF(noncolin) THEN
      ALLOCATE( aux_nc(npwx,npol) )
   ELSE
      ALLOCATE( aux(npwx) )
   ENDIF

   IF (gamma_only) ALLOCATE(aux2(npwx))


   !
   !   USPP
   !
   !
   IF(any_uspp) THEN
      CALL init_us_1
      CALL allocate_bec_type ( nkb, nbnd, becp )
      IF (gamma_only) THEN
         ALLOCATE ( rbecp2(nkb,nbnd))
!!!!!!!!!!!!!!!!!!!!!! USPP NC !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      ELSEIF(noncolin)THEN
         ALLOCATE ( becp2_nc(nkb,2,nbnd) )
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      ELSE
         ALLOCATE ( becp2(nkb,nbnd) )
      ENDIF
   ENDIF
   !
   !     qb is  FT of Q(r)
   !
   nbt = nnb * iknum
   !
   ALLOCATE( qg(nbt) )
   ALLOCATE (dxk(3,nbt))
   !
   ind = 0
   DO ik=1,iknum
      DO ib=1,nnb
         ind = ind + 1
         ikp = kpb(ik,ib)
         !
         g_(:) = REAL( g_kpb(:,ik,ib) )
         CALL cryst_to_cart (1, g_, bg, 1)
         dxk(:,ind) = xk(:,ikp) +g_(:) - xk(:,ik)
         qg(ind) = dxk(1,ind)*dxk(1,ind)+dxk(2,ind)*dxk(2,ind)+dxk(3,ind)*dxk(3,ind)


      ENDDO
!      write (stdout,'(i3,12f8.4)')  ik, qg((ik-1)*nnb+1:ik*nnb)
   ENDDO
   !
   !  USPP
   !
   IF(any_uspp) THEN

      ALLOCATE( ylm(nbt,lmaxq*lmaxq), qgm(nbt) )
      ALLOCATE( qb (nkb, nkb, ntyp, nbt) )
      !
      CALL ylmr2 (lmaxq*lmaxq, nbt, dxk, qg, ylm)
      qg(:) = sqrt(qg(:)) * tpiba
      !
      DO nt = 1, ntyp
         IF (upf(nt)%tvanp ) THEN
            DO ih = 1, nh (nt)
               DO jh = 1, nh (nt)
                  CALL qvan2 (nbt, ih, jh, nt, qg, qgm, ylm)
                  qb (ih, jh, nt, 1:nbt) = omega * qgm(1:nbt)
               ENDDO
            ENDDO
         ENDIF
      ENDDO
      !
      DEALLOCATE (qg, qgm, ylm )
      !
   ENDIF

   !

   ind = 0
   ! take care of non symmorphic case 
   ftau_=0
   non_symmorphic=.false.
   if(isym.ne.0)then
      WRITE(stdout,'(a)') '  Rotate wfct. '
      ftau_=ftau(:,isym)
   endif
   if(ftau_(1).ne.0 .or. ftau_(2).ne.0  .or. ftau_(3).ne.0 ) non_symmorphic=.true.
!   if(non_symmorphic) then
!         iktot=2*iknum ! need to go around the loop twice !
!   else
         iktot=iknum
!   endif
   ! file header
   iun_mmn = find_free_unit()
   IF (ionode) OPEN (unit=iun_mmn, file=trim(seedname)//".mmn",form='formatted')
   iun_i = find_free_unit()
   IF (ionode) OPEN (unit=iun_i, file=trim(seedname)//"_bands_pi.dat",form='formatted')
   iun_mi = find_free_unit()
   IF (ionode) OPEN (unit=iun_mi, file=trim(seedname)//"_bands_mi.dat",form='formatted')
   CALL date_and_tim( cdate, ctime )
   header='Created on '//cdate//' at '//ctime
   IF (ionode) THEN
      WRITE (iun_mmn,*) header
      WRITE (iun_mmn,*) nbnd-nexband-nexsym, iktot, nnb
   ENDIF
   ! rotate
   do ik=1,iknum
      ikevc = ik + ikstart - 1
      CALL davcio (evc, 2*nwordwfc, iunwfc, ikevc, -1 )
      CALL gk_sort (xk(1,ik), ngm, g, ecutwfc / tpiba2, npw, igk, g2kin)
      if(isym.ne.0)then
        CALL SYMPROJ(isym,ik,evc)
      endif
      evck(:,:,ik)=evc
   enddo
   ! compute MMN
   WRITE(stdout,*)
   WRITE(stdout,'(a,i8)') '  MMN: iknum = ',iknum
   !
   ALLOCATE( Mkb(nbnd,nbnd) )
   !
   DO jk=1,iktot
      WRITE (stdout,'(i8)',advance='no') jk
      IF( MOD(jk,10) == 0 ) WRITE (stdout,*)
      FLUSH(stdout)

!      if(non_symmorphic.and.jk>iknum)then 
!         ik=jk-iknum ! loop a second time on the other subspace
!         excluded_syma=.not.excluded_sym
!      else
         ik=jk
         excluded_syma=excluded_sym
!      endif

      ikevc = ik + ikstart - 1
!     CALL davcio (evc, 2*nwordwfc, iunwfc, ikevc, -1 )
      evc=evck(:,:,ik)
      CALL gk_sort (xk(1,ik), ngm, g, ecutwfc / tpiba2, npw, igk, g2kin)
      !
      !  USPP
      !
      IF(any_uspp) THEN
         CALL init_us_2 (npw, igk, xk(1,ik), vkb)
         ! below we compute the product of beta functions with |psi>
         CALL calbec (npw, vkb, evc, becp)
      ENDIF
      DO ib=1,nnb
         ind = ind + 1
         ikp = kpb(ik,ib)
!        index of neighbor  kpoints  if in second loop  (needed for mmn file only)
!         if(non_symmorphic)then
!      might be a simpler way of doing this....
!             if(jk==1.and.ikp==iknum)then
!                  jkp=iktot
!             elseif(jk==iknum.and.ikp==1)then
!                  jkp=iknum+1
!             elseif(jk==iknum+1.and.ikp==iknum)then 
!                  jkp=iknum         
!             elseif(jk>iknum.and.jk<2*iknum)then 
!                  jkp=iknum+ikp
!             elseif(jk==2*iknum.and.ikp==iknum-1)then
!                  jkp=2*iknum-1
!             else
!                  jkp=ikp
!             endif 
!         else  
             jkp=ikp
!         endif
!        non symmorphic case
!        at the zone border, the symmetry subspace are switched
!         if(dot_product(g_kpb(:,ik,ib),ftau_).ne.0 )then
!            excluded_symb=.not.excluded_syma
!         else
            excluded_symb=excluded_syma
!         endif
         ! read wfc at k+b
         ikpevcq = ikp + ikstart - 1
!        CALL davcio (evcq, 2*nwordwfc, iunwfc, ikpevcq, -1 )
         evcq=evck(:,:,ikp)
         CALL gk_sort (xk(1,ikp), ngm, g, ecutwfc / tpiba2, npwq, igkq, g2kin)
         ! compute the phase
         phase(:) = (0.d0,0.d0)
         IF ( ig_(ik,ib)>0) phase( nls(ig_(ik,ib)) ) = (1.d0,0.d0)
         CALL invfft ('Wave', phase, dffts)
         !
         !  USPP
         !
         IF(any_uspp) THEN
            CALL init_us_2 (npwq, igkq, xk(1,ikp), vkb)
            ! below we compute the product of beta functions with |psi>
            IF (gamma_only) THEN
               CALL calbec ( npwq, vkb, evcq, rbecp2 )
!!!!!!!!!!!!!!!!!!!!! USPP NC !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            ELSEIF(noncolin)THEN
               CALL calbec ( npwq, vkb, evcq, becp2_nc )
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            ELSE
               CALL calbec ( npwq, vkb, evcq, becp2 )
            ENDIF
         ENDIF
         !
         !
         Mkb(:,:) = (0.0d0,0.0d0)
         !
         IF (any_uspp) THEN
            ijkb0 = 0
            DO nt = 1, ntyp
               IF ( upf(nt)%tvanp ) THEN
                  DO na = 1, nat
                     !
                     arg = dot_product( dxk(:,ind), tau(:,na) ) * tpi
                     phase1 = cmplx( cos(arg), -sin(arg) ,kind=DP)
                     !
                     IF ( ityp(na) == nt ) THEN
                        DO jh = 1, nh(nt)
                           jkb = ijkb0 + jh
                           DO ih = 1, nh(nt)
                              ikb = ijkb0 + ih
                              !
                              DO m = 1,nbnd
                                 IF (excluded_band(m).or.excluded_syma(m)) CYCLE
                                 IF (gamma_only) THEN
                                    DO n=1,m ! Mkb(m,n) is symmetric in m and n for gamma_only case
                                       IF (excluded_band(n).or.excluded_syma(n)) CYCLE
                                       Mkb(m,n) = Mkb(m,n) + &
                                            phase1 * qb(ih,jh,nt,ind) * &
                                            becp%r(ikb,m) * rbecp2(jkb,n)
                                    ENDDO
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! USPP NC !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!! probably not correct after sym proj ..... becp has to be rotated too ....
                                 ELSEIF(noncolin)THEN
                               !    spin-orbit case                                   
                                    IF(upf(nt)%has_so)THEN
                                       ALLOCATE ( be1(nkb,2) )
                                       ALLOCATE ( be2(nkb,2) )
                                       DO n=1,nbnd
                                         IF(excluded_band(n).or.excluded_symb(n)) CYCLE
                                         be1=(0.d0,0.d0)
                                         be2=(0.d0,0.d0)
!                                        compute be1 for channel ih and band m
                                         DO kh=1,nh(nt)    ! loop on  beta channel kh - see localdos.f90 
                                           IF ((nhtol(kh,nt)==nhtol(ih,nt)).and.&
                                               (nhtoj(kh,nt)==nhtoj(ih,nt)).and.&
                                               (indv(kh,nt)==indv(ih,nt))) THEN
                                                 DO is1=1,2
                                                 DO is2=1,2
                                                      be1(ikb,is1)=be1(ikb,is1)+&
                                                       fcoef(ih,kh,is1,is2,nt)*becp%nc(ikb,is2,m)
                                                 ENDDO
                                                 ENDDO
                                           ENDIF
                                         ENDDO
!                                        compute be2 for channel jh and band n
                                         DO kh=1,nh(nt)    ! loop on  beta channel kh - see localdos.f90 
                                           IF ((nhtol(kh,nt)==nhtol(jh,nt)).and.&
                                               (nhtoj(kh,nt)==nhtoj(jh,nt)).and.&
                                               (indv(kh,nt)==indv(jh,nt))) THEN
                                                 DO is1=1,2
                                                 DO is2=1,2
                                                      be2(jkb,is1)=be2(jkb,is1)+&
                                                        fcoef(jh,kh,is1,is2,nt)*becp2_nc(jkb,is2,n)
                                                 ENDDO
                                                 ENDDO
                                           ENDIF
                                         ENDDO
!                                      compute Mkb(m,n)
                                         Mkb(m,n) = Mkb(m,n) + &
                                         phase1 * qb(ih,jh,nt,ind) * (&
                                         conjg( be1(ikb,1 ) ) * be2(jkb,1 )+&
                                         conjg( be1(ikb,2 ) ) * be2(jkb,2 ))
                                      ENDDO
                                      DEALLOCATE(be1,be2)
                                    ELSE
                                 !!   no spin-orbit case
                                      DO n=1,nbnd
                                       IF (excluded_band(n)) CYCLE
                                       Mkb(m,n) = Mkb(m,n) + &
                                            phase1 * qb(ih,jh,nt,ind) * (&
                                            conjg( becp%nc(ikb,1,m ) ) * becp2_nc(jkb,1,n )+&
                                            conjg( becp%nc(ikb,2,m ) ) * becp2_nc(jkb,2,n ))

                                      ENDDO
                                    ENDIF
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                                 ELSE
                                    DO n=1,nbnd
                                       IF (excluded_band(n).or.excluded_symb(n)) CYCLE
                                       Mkb(m,n) = Mkb(m,n) + &
                                            phase1 * qb(ih,jh,nt,ind) * &
                                            conjg( becp%k(ikb,m) ) * becp2(jkb,n)
                                    ENDDO
                                 ENDIF
                              ENDDO ! m
                           ENDDO !ih
                        ENDDO !jh
                        ijkb0 = ijkb0 + nh(nt)
                     ENDIF  !ityp
                  ENDDO  !nat
               ELSE  !tvanp
                  DO na = 1, nat
                     IF ( ityp(na) == nt ) ijkb0 = ijkb0 + nh(nt)
                  ENDDO
               ENDIF !tvanp
            ENDDO !ntyp
         ENDIF ! any_uspp
         !
         !
! loops on bands
         !
         IF (ionode) WRITE (iun_mmn,'(7i5)') jk, jkp, (g_kpb(ipol,ik,ib), ipol=1,3)
         !
         DO m=1,nbnd
            IF (excluded_band(m).or.excluded_syma(m)) CYCLE
            !
            IF(noncolin) THEN
               psic_nc(:,:) = (0.d0, 0.d0)
               DO ipol=1,2!npol
                  istart=(ipol-1)*npwx+1
                  iend=istart+npw-1
                  psic_nc(nls (igk (1:npw) ),ipol ) = evc(istart:iend, m)
                  CALL invfft ('Wave', psic_nc(:,ipol), dffts)
                  psic_nc(1:dffts%nnr,ipol) = psic_nc(1:dffts%nnr,ipol) * &
                                                 phase(1:dffts%nnr)
                  CALL fwfft ('Wave', psic_nc(:,ipol), dffts)
                  aux_nc(1:npwq,ipol) = psic_nc(nls (igkq(1:npwq) ),ipol )
               ENDDO
            ELSE
               psic(:) = (0.d0, 0.d0)
               psic(nls (igk (1:npw) ) ) = evc (1:npw, m)
               IF(gamma_only) psic(nlsm(igk (1:npw) ) ) = conjg(evc (1:npw, m))
               CALL invfft ('Wave', psic, dffts)
               psic(1:dffts%nnr) = psic(1:dffts%nnr) * phase(1:dffts%nnr)
               CALL fwfft ('Wave', psic, dffts)
               aux(1:npwq)  = psic(nls (igkq(1:npwq) ) )
            ENDIF
            IF(gamma_only) THEN
               IF (gstart==2) psic(nlsm(1)) = (0.d0,0.d0)
               aux2(1:npwq) = conjg(psic(nlsm(igkq(1:npwq) ) ) )
            ENDIF
            !
            !  Mkb(m,n) = Mkb(m,n) + \sum_{ijI} qb_{ij}^I * e^-i(b*tau_I)
            !             <psi_m,k1| beta_i,k1 > < beta_j,k2 | psi_n,k2 >
            !
            IF (gamma_only) THEN
               DO n=1,m ! Mkb(m,n) is symmetric in m and n for gamma_only case
                  IF (excluded_band(n).or.excluded_symb(n)) CYCLE
                  mmn = zdotc (npwq, aux,1,evcq(1,n),1) &
                       + conjg(zdotc(npwq,aux2,1,evcq(1,n),1))
                  CALL mp_sum(mmn, intra_pool_comm)
                  Mkb(m,n) = mmn + Mkb(m,n)
                  IF (m/=n) Mkb(n,m) = Mkb(m,n) ! fill other half of matrix by symmetry
               ENDDO
            ELSEIF(noncolin) THEN
               DO n=1,nbnd
                  IF (excluded_band(n).or.excluded_symb(n)) CYCLE
                  mmn=(0.d0, 0.d0)
!                      write(*,*) ik,ikp,m,n 
!                  do ipol=1,2
!                     mmn = mmn+zdotc (npwq, aux_nc(1,ipol),1,evcq_nc(1,ipol,n),1)
                  mmn = mmn + zdotc (npwq, aux_nc(1,1),1,evcq(1,n),1) &
                       + zdotc (npwq, aux_nc(1,2),1,evcq(npwx+1,n),1)
!                  end do
                  CALL mp_sum(mmn, intra_pool_comm)
                  Mkb(m,n) = mmn + Mkb(m,n)
               ENDDO
            ELSE
               DO n=1,nbnd
                  IF (excluded_band(n).or.excluded_symb(n)) CYCLE
                  mmn = zdotc (npwq, aux,1,evcq(1,n),1)
                  CALL mp_sum(mmn, intra_pool_comm)
                  Mkb(m,n) = mmn + Mkb(m,n)
               ENDDO
            ENDIF
         ENDDO   ! m

! extra phase in non_symmorphic case !!!!!!!!!!!!!!!!!!!!!!!!!
! WRONG
!        IF(non_symmorphic.and.(n>nexsym.or.m>nexsym))THEN
!                Mkb(m,n)=-1.0d0*Mkb(m,n)
!        ENDIF
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
         ibnd_n = 0
         DO n=1,nbnd
            IF (excluded_band(n).or.excluded_symb(n)) CYCLE
            ibnd_n = ibnd_n + 1
            ibnd_m = 0
            DO m=1,nbnd
               IF (excluded_band(m).or.excluded_syma(m)) CYCLE
               ibnd_m = ibnd_m + 1
               IF (ionode) WRITE (iun_mmn,'(2f18.12)') Mkb(m,n)
            ENDDO
         ENDDO
 
      ENDDO !ib
   ENDDO  !ik

   
   IF (ionode) CLOSE (iun_mmn)

   IF (gamma_only) DEALLOCATE(aux2)
   DEALLOCATE (Mkb, dxk, phase, igkq)
   IF(noncolin) THEN
      DEALLOCATE(aux_nc)
   ELSE
      DEALLOCATE(aux)
   ENDIF
   DEALLOCATE(evcq)

   IF(any_uspp) THEN
      DEALLOCATE (  qb)
      CALL deallocate_bec_type (becp)
      IF (gamma_only) THEN
          DEALLOCATE (rbecp2)
!!!!!!!!!!!!!!!! USPP NC !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       ELSEIF(noncolin)THEN
          DEALLOCATE(becp2_nc)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       ELSE
          DEALLOCATE (becp2)
       ENDIF
    ENDIF
!
   WRITE(stdout,*)
   WRITE(stdout,*) ' MMN calculated'

   CALL stop_clock( 'compute_mmn' )

   RETURN
END SUBROUTINE compute_mmn


SUBROUTINE SYMPROJ(isym,ik,evc)
  USE io_global,        ONLY : stdout, ionode
  USE kinds,            ONLY : dp
  USE cell_base,        ONLY : at
  USE klist,            ONLY : xk
  USE symm_base,        ONLY : s,sr,ftau, nsym,sname,ft
  USE z2pack,           ONLY : nexband,num_bands,excluded_sym,sym_eig,nexsym,excluded_band,iun_mi,iun_i,tr,sym_thr,deg_thr
  USE constants,        ONLY : tpi,RYTOEV
  USE wvfct,            ONLY : nbnd, npw, npwx,et
  USE noncollin_module, ONLY : npol
  USE mp_bands,         ONLY : intra_bgrp_comm
  USE mp,               ONLY : mp_sum
!  USE wvfct,                ONLY :  et
!  USE constants, ONLY : RYTOEV
!==
  IMPLICIT NONE
!! INPUT
  INTEGER     ::   isym,ik
!! INPUT-OUTPUT
  COMPLEX(DP) ::   evc(npol*npwx,nbnd) 
!! LOCAL
  LOGICAL     non_symmorphic
  LOGICAL,    ALLOCATABLE :: done(:)
  INTEGER     i,j,k,ipol,jpol,istart,iend,ibnd,m,n,ngroup,ip,im,igroup,ng
  INTEGER     s_(3,3),ftau_(3),gk(3),imi,ipi
  INTEGER     has_e
  INTEGER,    ALLOCATABLE :: group(:,:),groupsize(:)
  REAL(DP)    ak(3),rak(3),zero
  REAL(DP)    sr_(3,3) ,ft_(3),ftau_zero(3)
  COMPLEX(DP) d_spin(2,2,64),d_spin_(2,2),m1,tphase
  COMPLEX(DP),ALLOCATABLE :: evcr(:,:),psitmp(:,:)
  COMPLEX(DP),ALLOCATABLE :: symdensity(:,:),sym(:)
! LAPACK
  INTEGER INFO,LWORK
  REAL(DP)    , ALLOCATABLE :: rwork(:)
  COMPLEX(DP) , ALLOCATABLE :: EigenVal(:),vl(:,:),vr(:,:)
  COMPLEX(DP) , ALLOCATABLE :: WORK(:)
!! EXTERNAL
  COMPLEX(DP) :: zdotc
!==
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  non_symmorphic=.false.
  s_=s(:,:,isym)
  ftau_=ftau(:,isym)
! here we only keep the mirror part of the glide and sort by eigenvalues I*exp(i k ft_)  
  ft_=ft(:,isym)
  if(ftau_(1).ne.0 .or. ftau_(2).ne.0  .or. ftau_(3).ne.0 ) non_symmorphic=.true.
  sr_=sr(:,:,isym)
  CALL find_u(sr_,d_spin_)
  gk=0
! time reversal
  if(tr)then
   has_e=-1
   d_spin_=-d_spin_
  else
   has_e=1
  endif
!!!!!!!!!!!!!! compute gk !!!!!!!!!!!!!
  ak = xk(1:3,ik)
  CALL cryst_to_cart (1, ak, at, - 1)
  rak = 0.d0
  DO ipol = 1, 3
    DO jpol = 1, 3
      rak (ipol) = rak (ipol) + dble (s_ (ipol, jpol) ) * &
           ak (jpol)
    ENDDO
  ENDDO
!! check that k is symmetric under isym
  IF(ionode)THEN
   DO ipol=1,3
     if(abs(mod((rak(ipol)-ak(ipol)),1.0)) >1d-3)then
       write(stdout,'("Warning: kpoint", i5," is not symmetric under,",a )') ik,sname(isym)
       write(stdout,'("   k=",3f10.4,"--> rk=",3f10.4 )') ak,rak
!       stop
     endif
   ENDDO
  ENDIF
!! gk
  gk(:)=nint(rak(:)-ak(:))
!! translation phase
  tphase=exp((0.0d0,1.0d0)*tpi*dot_product(ak,ft_))

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!write(*,*) ik,ak,rak,gk
!!!!!!!!!!!!!! summary !!!!!!!!!!!!!!!!
  if(ionode)then
   write(stdout,'("#======================================")')
   write(stdout,'("# kpoint=",i5)') ik
   write(stdout,'("#  xk    =",3f16.8)') xk(1:3,ik)
   write(stdout,'("#  ak    =",3f16.8)') ak(1:3)
   write(stdout,'("#  rak   =",3f16.8)') rak(1:3)
   write(stdout,'("#")')
   write(stdout,'("# ",a)') sname(isym)
   write(stdout,'("# target sym eig=",2f16.8)') sym_eig
   write(stdout,'("# non_symmorphic: ",l)')    non_symmorphic 
   write(stdout,'("#")')
   write(stdout,'("#  s     =",3i5)') s_
   write(stdout,'("#  ftau  =",3i5)') ftau_
   write(stdout,'("#  ft    =",3f16.8)') ft_
   write(stdout,'("#  tphase=",2f16.8)') tphase
   write(stdout,'("#  gk    =",3i5)') gk
   write(stdout,'("#  d_spin=",4f16.8)') d_spin_
   write(stdout,'("#")')
!   write(stdout,'("# WARNING: this works only for doubly degenerate case ....")')
  endif
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! find degeneracies
  ngroup=0
  ALLOCATE(groupsize(num_bands),group(num_bands,num_bands),done(num_bands))
  groupsize=0
  group=0
  done=.false.
  do i=1,num_bands
    if(.not.done(i))then
     ngroup=ngroup+1
     igroup=1     
     groupsize(ngroup)=groupsize(ngroup)+1
     group(igroup,ngroup)=i
     done(i)=.true.
     do j=i+1,num_bands
       if(abs(et(i+nexband,ik)-et(j+nexband,ik))<deg_thr)then
         igroup=igroup+1
         groupsize(ngroup)=groupsize(ngroup)+1
         group(igroup,ngroup)=j
         done(j)=.true.
       endif
     enddo
    endif    
  enddo
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! allocation
  ALLOCATE(evcr(npwx*npol,nbnd))
  ALLOCATE(sym(num_bands))
  evcr=0.d0
! rotate wavefunctions
! R |psi_i>
  CALL rotate_all_psi_so(evc,evcr,s_,        &
                         ftau_,d_spin_,has_e,gk)
! rotate each degenrate group into sym subspace 
  do igroup=1,ngroup
    ng=groupsize(igroup)
    ALLOCATE(symdensity(ng,ng))
    do i=1,groupsize(igroup)
     do j=1,groupsize(igroup)
        symdensity(i,j)=zdotc(2*npwx,evc(1,group(i,igroup)+nexband),1,evcr(1,group(j,igroup)+nexband),1)
     enddo
   enddo
  CALL mp_sum(symdensity,intra_bgrp_comm)
  if(ng>1)then ! rotate
! diagonalize matrix <psi_i | R | psi_j>
   LWORK=2*ng
   allocate(eigenval(ng),vl(ng,ng),vr(ng,ng),rwork(lwork),work(lwork))
   CALL ZGEEV( 'N', 'V',ng, symdensity, ng, Eigenval,  VL, ng, VR, ng, WORK, LWORK,   RWORK, INFO)
   ALLOCATE(psitmp(npwx*npol,ng))
   psitmp=evc(:,group(1,igroup)+nexband:group(ng,igroup)+nexband)
   do i=1,ng
     m=group(i,igroup)+nexband
     evc(:,m)=0.0d0
     do j=1,ng   
        evc(:,m)=evc(:,m) + VR(j,i)*psitmp(:,j)       
     enddo
     sym(group(i,igroup))=eigenval(i)
   enddo
   deallocate(eigenval,vl,vr,rwork,work,psitmp)
  else
   sym(group(1,igroup))=symdensity(1,1)
  endif

  deallocate(symdensity)
  enddo ! igroup
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

  if(ionode)then
   imi=0
   ipi=0
   do i=1,num_bands
    write(stdout,'("#  sym eig ",i5,"=",2f16.8)') i,sym(i) 
    IF(aimag(sym(i))<0.0d0)THEN
      imi=imi+1 
      write(iun_mi,'(i5,f16.8,2e16.8,2i5)') ik,et(i+nexband,ik)*RYTOEV,sym(i),i+nexband,imi
    ELSE
      ipi=ipi+1 
       write(iun_i,'(i5,f16.8,2e16.8,2i5)') ik,et(i+nexband,ik)*RYTOEV,sym(i),i+nexband,ipi
    ENDIF
   enddo
  endif
! check U is unitary
!  VL=transpose(conjg(VR))
!  VL=matmul(VL,VR)
!  do i=1,nbnd
!    write(*,'(i5,40f10.4)') i,VL(i,:)
!  enddo
! rotate {|psi_i>}  
!  evcr=evc
!  do m=1,num_bands
!    evc(:,m+nexband)=0.0d0
!    do i=1,num_bands
!      evc(:,m+nexband)=evc(:,m+nexband)+VR(i,m)*evcr(:,i+nexband)
!    enddo
!  enddo
! sort by eigenvalue
  evcr=evc
  i=0
  excluded_sym=.false.
  do m=1,num_bands  
     if(abs(sym(m)-sym_eig)<=sym_thr)then
      i=i+1
      evcr(:,i+nexband)=evc(:,m+nexband)
     endif    
  enddo 
! check that we found he correct number of symmetric states
  if(ionode.and.i.ne.nexsym)then
    write(stdout,'(a,i5,a,2f16.8,a,i5)') "Error: found ",i," states with sym eig=",sym_eig, " for kpoint ",ik
    write(stdout,'(a,i5,a)')        " -->expecting ",nexsym," states."
    write(stdout,'(a,a)')           " Check that the plane is symmetric under ",sname(isym)
    write(stdout,'(a,2f16.8,a)')    " and that ",sym_eig," is a symmetry eigenvalue."
    stop
  endif

  do m=1,num_bands
     if(abs(sym(m)-sym_eig)>1d-3)then
      i=i+1
      evcr(:,i+nexband)=evc(:,m+nexband)
      excluded_sym(i+nexband)=.true.
     endif    
  enddo 
  evc=evcr
!
! uncomment to check that the excluded bands and the subspace are correct
!
!  ftau_zero=0.0d0
!  CALL rotate_all_psi_so(evc,evcr,s_,        &
!                         ftau_,d_spin_,has_e,gk)
!  do m=1,nbnd
!    m1=zdotc(2*npwx,evc(1,m),1,evcr(1,m),1)
!    CALL mp_sum(m1,intra_bgrp_comm)
!    write(*,'("#  ",i5,2f16.8," ",l,l)') m,m1,.not.excluded_sym(m),.not.excluded_band(M)
!  enddo
!  deallocate
!  deallocate(evcr,eigenval,symdensity,vr,vl,work,rwork)  
  deallocate(evcr)
END SUBROUTINE SYMPROJ


SUBROUTINE rotate_all_psi_so(evc_nc,evcr,s,ftau,d_spin,has_e,gk)
  !
  !  This subroutine rotates a spinor wavefunction according to the symmetry
  !  s. d_spin contains the 2x2 rotation matrix in the spin space.
  !  has_e=-1 means that also a 360 degrees rotation is applied in spin space.
  !
  USE kinds,     ONLY : DP
  USE constants, ONLY : tpi
  USE fft_base,  ONLY : dfftp
  USE scatter_mod,  ONLY : cgather_sym_many, cscatter_sym_many
  USE fft_interfaces, ONLY : fwfft, invfft
  USE gvect,     ONLY : ngm, nl
  USE wvfct,     ONLY : nbnd, npwx, npw, igk
  USE noncollin_module, ONLY : npol
  USE mp_bands,  ONLY : intra_bgrp_comm
  USE mp,        ONLY : mp_sum

  IMPLICIT NONE

  INTEGER :: s(3,3), ftau(3), gk(3), has_e
  COMPLEX(DP) :: evc_nc(npwx,2,nbnd), evcr(npwx,2,nbnd), d_spin(2,2)

  COMPLEX(DP), ALLOCATABLE :: psic(:,:), psir(:), evcr_save(:,:,:)
  COMPLEX(DP) :: phase
  REAL(DP) :: arg
  INTEGER :: i, j, k, ri, rj, rk, ir, rir, ipol, jpol, ibnd
  INTEGER :: nr1, nr2, nr3, nr1x, nr2x, nr3x, nrxx
  LOGICAL :: zone_border
  INTEGER :: start_band, last_band, my_nbnd_proc
  INTEGER :: start_band_proc(dfftp%nproc), nbnd_proc(dfftp%nproc)
  !
#if defined  (__MPI)
  !
  COMPLEX (DP), ALLOCATABLE :: psir_collect(:)
  COMPLEX (DP), ALLOCATABLE :: psic_collect(:,:)
  !
#endif

!do i=1,nbnd
!  write(*,*) 'all spin1', evc_nc(1,1,i)
!  write(*,*) 'all spin2', evc_nc(1,2,i)
!enddo

  nr1=dfftp%nr1
  nr2=dfftp%nr2
  nr3=dfftp%nr3
  nr1x=dfftp%nr1x
  nr2x=dfftp%nr2x
  nr3x=dfftp%nr3x
  nrxx=dfftp%nnr


#if defined  (__MPI)
  call divide (intra_bgrp_comm, nbnd, start_band, last_band)
  start_band_proc=0
  start_band_proc(dfftp%mype+1)=start_band
  nbnd_proc=0
  my_nbnd_proc=last_band-start_band+1
  nbnd_proc(dfftp%mype+1)=my_nbnd_proc
  CALL mp_sum(start_band_proc, intra_bgrp_comm)
  CALL mp_sum(nbnd_proc, intra_bgrp_comm)
  ALLOCATE (psic_collect(nr1x*nr2x*nr3x,my_nbnd_proc))
  ALLOCATE (psir_collect(nr1x*nr2x*nr3x))
#endif
  !
  ALLOCATE(psic(nrxx,nbnd))
  ALLOCATE(psir(nrxx))
  ALLOCATE(evcr_save(npwx,npol,nbnd))
  !
  zone_border=(gk(1)/=0.or.gk(2)/=0.or.gk(3)/=0)
  !
  !
  DO ipol=1,npol
     !
     psic = ( 0.D0, 0.D0 )
     psir = ( 0.D0, 0.D0 )
     !
     DO ibnd=1,nbnd
        psic(nl(igk(1:npw)),ibnd) = evc_nc(1:npw,ipol,ibnd)
        CALL invfft ('Dense', psic(:,ibnd), dfftp)
     ENDDO
     !
#if defined  (__MPI)
     !
     !
     CALL cgather_sym_many( dfftp, psic, psic_collect, nbnd, nbnd_proc, &
                                                       start_band_proc  )
     !
     psir_collect=(0.d0,0.d0)
     DO ibnd=1,my_nbnd_proc
        !
        IF (zone_border) THEN
           DO k = 1, nr3
              DO j = 1, nr2
                 DO i = 1, nr1
                    CALL ruotaijk (s, ftau, i, j, k, nr1, nr2, nr3, ri, rj, rk )
                    ir=i+(j-1)*nr1x+(k-1)*nr1x*nr2x
                    rir=ri+(rj-1)*nr1x+(rk-1)*nr1x*nr2x
                    arg=tpi*( (gk(1)*(i-1))/dble(nr1)+(gk(2)*(j-1))/dble(nr2)+ &
                         (gk(3)*(k-1))/dble(nr3) )
                    phase=cmplx(cos(arg),sin(arg),kind=DP)
                    psir_collect(ir)=psic_collect(rir,ibnd)*phase
                 ENDDO
              ENDDO
           ENDDO
        ELSE
           DO k = 1, nr3
              DO j = 1, nr2
                 DO i = 1, nr1
                    CALL ruotaijk (s, ftau, i, j, k, nr1, nr2, nr3, ri, rj, rk )
                    ir=i+(j-1)*nr1x+(k-1)*nr1x*nr2x
                    rir=ri+(rj-1)*nr1x+(rk-1)*nr1x*nr2x
                    psir_collect(ir)=psic_collect(rir,ibnd)
                 ENDDO
              ENDDO
           ENDDO
        ENDIF
        psic_collect(:,ibnd) = psir_collect(:)
     ENDDO
     DO ibnd=1,nbnd
        !
        CALL cscatter_sym_many(dfftp, psic_collect, psir, ibnd, nbnd, nbnd_proc, &
                               start_band_proc)
        CALL fwfft ('Dense', psir, dfftp)
        !
        evcr_save(1:npw,ipol,ibnd) = psir(nl(igk(1:npw)))
     ENDDO
     !
#else
     DO ibnd=1,nbnd
        IF (zone_border) THEN
           DO k = 1, nr3
              DO j = 1, nr2
                 DO i = 1, nr1
                    CALL ruotaijk (s, ftau, i, j, k, nr1, nr2, nr3, ri, rj, rk )
                    ir=i+(j-1)*nr1x+(k-1)*nr1x*nr2x
                    rir=ri+(rj-1)*nr1x+(rk-1)*nr1x*nr2x
                    arg=tpi*( (gk(1)*(i-1))/dble(nr1)+(gk(2)*(j-1))/dble(nr2)+ &
                         (gk(3)*(k-1))/dble(nr3) )
                    phase=cmplx(cos(arg),sin(arg),kind=DP)
                    psir(ir)=psic(rir,ibnd)*phase
                 ENDDO
              ENDDO
           ENDDO
        ELSE
           DO k = 1, nr3
              DO j = 1, nr2
                 DO i = 1, nr1
                    CALL ruotaijk (s, ftau, i, j, k, nr1, nr2, nr3, ri, rj, rk )
                    ir=i+(j-1)*nr1x+(k-1)*nr1x*nr2x
                    rir=ri+(rj-1)*nr1x+(rk-1)*nr1x*nr2x
                    psir(ir)=psic(rir,ibnd)
                 ENDDO
              ENDDO
           ENDDO
        ENDIF
        CALL fwfft ('Dense', psir(:), dfftp)
        !
        evcr_save(1:npw,ipol,ibnd) = psir(nl(igk(1:npw)))
     ENDDO
     !
#endif
     !
     !
  ENDDO


  evcr=(0.d0,0.d0)
  DO ibnd=1,nbnd 
     DO ipol=1,npol
        DO jpol=1,npol
           evcr(:,ipol,ibnd)=evcr(:,ipol,ibnd)+ &
                conjg(d_spin(jpol,ipol))*evcr_save(:,jpol,ibnd)
        ENDDO
     ENDDO
  ENDDO
  IF (has_e==-1) evcr=-evcr
  !
!do i=1,nbnd
!  write(*,*) 'all spin1 r', evcr(1,1,i)
!  write(*,*) 'all spin2 r', evcr(1,2,i)
!enddo

  DEALLOCATE(evcr_save)
  DEALLOCATE(psic)
  DEALLOCATE(psir)
#if defined (__MPI)
  DEALLOCATE (psic_collect)
  DEALLOCATE (psir_collect)
#endif
  RETURN
END SUBROUTINE rotate_all_psi_so

