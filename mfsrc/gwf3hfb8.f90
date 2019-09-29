
module GwfHfbModule

  use KindModule, only: DP, I4B
  use Xt3dModule,             only: Xt3dType
  use NumericalPackageModule, only: NumericalPackageType
  use BlockParserModule,      only: BlockParserType
  use BaseDisModule,          only: DisBaseType

  implicit none

  private
  public :: GwfHfbType
  public :: hfb_cr

  type, extends(NumericalPackageType) :: GwfHfbType
    integer(I4B), pointer :: maxhfb => null()                                    !max number of hfb's
    integer(I4B), pointer :: nhfb => null()                                      !number of hfb's
    integer(I4B), dimension(:), pointer, contiguous :: noden => null()           !first cell
    integer(I4B), dimension(:), pointer, contiguous :: nodem => null()           !second cell
    integer(I4B), dimension(:), pointer, contiguous :: idxloc => null()          !position in model ja
    real(DP), dimension(:), pointer, contiguous :: hydchr => null()              !hydraulic characteristic of the barrier
    real(DP), dimension(:), pointer, contiguous :: csatsav => null()             !value of condsat prior to hfb modification
    real(DP), dimension(:), pointer, contiguous :: condsav => null()             !saved conductance of combined npf and hfb
    type(Xt3dType), pointer :: xt3d => null()                                    !pointer to xt3d object
    !
    integer(I4B), dimension(:), pointer, contiguous :: ibound  => null()         !pointer to model ibound
    integer(I4B), dimension(:), pointer, contiguous :: icelltype => null()       !pointer to model icelltype
    integer(I4B), dimension(:), pointer, contiguous :: ihc => null()             !pointer to model ihc
    integer(I4B), dimension(:), pointer, contiguous :: ia  => null()             !pointer to model ia
    integer(I4B), dimension(:), pointer, contiguous :: ja => null()              !pointer to model ja
    integer(I4B), dimension(:), pointer, contiguous :: jas => null()             !pointer to model jas
    integer(I4B), dimension(:), pointer, contiguous :: isym => null()            !pointer to model isym
    real(DP), dimension(:), pointer, contiguous :: condsat => null()             !pointer to model condsat
    real(DP), dimension(:), pointer, contiguous :: top => null()                 !pointer to model top
    real(DP), dimension(:), pointer, contiguous :: bot => null()                 !pointer to model bot
    real(DP), dimension(:), pointer, contiguous :: hwva => null()                !pointer to model hwva
  contains
    procedure :: hfb_ar
    procedure :: hfb_rp
    procedure :: hfb_fc
    procedure :: hfb_flowja
    procedure :: hfb_da
    procedure          :: allocate_scalars
    procedure, private :: allocate_arrays
    procedure, private :: read_options
    procedure, private :: read_dimensions
    procedure, private :: read_data
    procedure, private :: check_data
    procedure, private :: condsat_reset
    procedure, private :: condsat_modify
  end type GwfHfbType

  contains

  subroutine hfb_cr(hfbobj, name_model, inunit, iout)
! ******************************************************************************
! hfb_cr -- Create a new hfb object
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    type(GwfHfbType), pointer :: hfbobj
    character(len=*), intent(in) :: name_model
    integer(I4B), intent(in) :: inunit
    integer(I4B), intent(in) :: iout
! ------------------------------------------------------------------------------
    !
    ! -- Create the object
    allocate(hfbobj)
    !
    ! -- create name and origin
    call hfbobj%set_names(1, name_model, 'HFB', 'HFB')
    !
    ! -- Allocate scalars
    call hfbobj%allocate_scalars()
    !
    ! -- Save unit numbers
    hfbobj%inunit = inunit
    hfbobj%iout = iout
    !
    ! -- Initialize block parser
    call hfbobj%parser%Initialize(hfbobj%inunit, hfbobj%iout)
    !
    ! -- Return
    return
  end subroutine hfb_cr

  subroutine hfb_ar(this, ibound, xt3d, dis)
! ******************************************************************************
! hfb_ar -- Allocate and read
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    use MemoryManagerModule, only: mem_setptr
    ! -- dummy
    class(GwfHfbType) :: this
    integer(I4B), dimension(:), pointer, contiguous :: ibound
    type(Xt3dType), pointer :: xt3d
    class(DisBaseType), pointer, intent(inout) :: dis
    ! -- formats
    character(len=*), parameter :: fmtheader =                                 &
      "(1x, /1x, 'HFB -- HORIZONTAL FLOW BARRIER PACKAGE, VERSION 8, ',        &
        '4/24/2015 INPUT READ FROM UNIT ', i4, //)"
! ------------------------------------------------------------------------------
    !
    ! -- Print a message identifying the node property flow package.
    write(this%iout, fmtheader) this%inunit
    !
    ! -- Set pointers
    this%dis => dis
    this%ibound => ibound
    this%xt3d => xt3d
    call mem_setptr(this%icelltype, 'ICELLTYPE', trim(adjustl(this%name_model))//' NPF')
    call mem_setptr(this%ihc, 'IHC', trim(adjustl(this%name_model))//' CON')
    call mem_setptr(this%ia, 'IA', trim(adjustl(this%name_model))//' CON')
    call mem_setptr(this%ja, 'JA', trim(adjustl(this%name_model))//' CON')
    call mem_setptr(this%jas, 'JAS', trim(adjustl(this%name_model))//' CON')
    call mem_setptr(this%isym, 'ISYM', trim(adjustl(this%name_model))//' CON')
    call mem_setptr(this%condsat, 'CONDSAT', trim(adjustl(this%name_model))//' NPF')
    call mem_setptr(this%top, 'TOP', trim(adjustl(this%name_model))//' DIS')
    call mem_setptr(this%bot, 'BOT', trim(adjustl(this%name_model))//' DIS')
    call mem_setptr(this%hwva, 'HWVA', trim(adjustl(this%name_model))//' CON')
    !
    call this%read_options()
    call this%read_dimensions()
    call this%allocate_arrays()
    !
    ! -- return
    return
  end subroutine hfb_ar

  subroutine hfb_rp(this)
! ******************************************************************************
! hfb_rp -- Check for new hfb stress period data
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    use ConstantsModule, only: LINELENGTH
    use SimModule, only: ustop, store_error, count_errors, store_error_unit
    use TdisModule, only: kper, nper
    ! -- dummy
    class(GwfHfbType) :: this
    ! -- local
    character(len=LINELENGTH) :: line, errmsg
    integer(I4B) :: ierr
    logical :: isfound
    ! -- formats
    character(len=*),parameter :: fmtblkerr = &
      "('Error.  Looking for BEGIN PERIOD iper.  Found ', a, ' instead.')"
    character(len=*),parameter :: fmtlsp = &
      "(1X,/1X,'REUSING ',A,'S FROM LAST STRESS PERIOD')"
! ------------------------------------------------------------------------------
    !
    ! -- Set ionper to the stress period number for which a new block of data
    !    will be read.
    if (this%ionper < kper) then
      !
      ! -- get period block
      call this%parser%GetBlock('PERIOD', isfound, ierr, &
                                supportOpenClose=.true.)
      if(isfound) then
        !
        ! -- read ionper and check for increasing period numbers
        call this%read_check_ionper()
      else
        !
        ! -- PERIOD block not found
        if (ierr < 0) then
          ! -- End of file found; data applies for remainder of simulation.
          this%ionper = nper + 1
        else
          ! -- Found invalid block
          write(errmsg, fmtblkerr) adjustl(trim(line))
          call store_error(errmsg)
          call this%parser%StoreErrorUnit()
          call ustop()
        end if
      endif
    end if
    !
    if(this%ionper == kper) then
      call this%condsat_reset()
      call this%read_data()
      call this%condsat_modify()
    else
      write(this%iout,fmtlsp) 'HFB'
    endif
    !
    ! -- return
    return
  end subroutine hfb_rp

  subroutine hfb_fc(this, kiter, nodes, nja, njasln, amat, idxglo, rhs, hnew)
! ******************************************************************************
! hfb_fc -- Fill amatsln for the following conditions:
!   1.  Not Newton, and
!   2.  Cell type n is convertible or cell type m is convertible
!  OR
!   3.  XT3D
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    use ConstantsModule, only: DHALF, DZERO
    ! -- dummy
    class(GwfHfbType) :: this
    integer(I4B) :: kiter
    integer(I4B),intent(in) :: nodes
    integer(I4B),intent(in) :: nja
    integer(I4B),intent(in) :: njasln
    real(DP),dimension(njasln),intent(inout) :: amat
    integer(I4B),intent(in),dimension(nja) :: idxglo
    real(DP),intent(inout),dimension(nodes) :: rhs
    real(DP),intent(inout),dimension(nodes) :: hnew
    ! -- local
    integer(I4B) :: ihfb, n, m
    integer(I4B) :: ipos
    integer(I4B) :: idiag, isymcon
    integer(I4B) :: ixt3d
    real(DP) :: cond, condhfb, aterm
    real(DP) :: fawidth, faheight
    real(DP) :: topn, topm, botn, botm
! ------------------------------------------------------------------------------
    !
    if (associated(this%xt3d%ixt3d)) then
      ixt3d = this%xt3d%ixt3d
    else
      ixt3d = 0
    end if
    !
    if(ixt3d > 0) then
      !
      do ihfb = 1, this%nhfb
        n = min(this%noden(ihfb), this%nodem(ihfb))
        m = max(this%noden(ihfb), this%nodem(ihfb))
        ! -- Skip if either cell is inactive.
        if(this%ibound(n) == 0 .or. this%ibound(m) == 0) cycle
  !!!      if(this%icelltype(n) == 1 .or. this%icelltype(m) == 1) then
        ! -- Compute scale factor for hfb correction
        if(this%hydchr(ihfb) > DZERO) then
          if(this%inewton == 0) then
            ipos = this%idxloc(ihfb)
            topn = this%top(n)
            topm = this%top(m)
            botn = this%bot(n)
            botm = this%bot(m)
            if(this%icelltype(n) == 1) then
              if(hnew(n) < topn) topn = hnew(n)
            endif
            if(this%icelltype(m) == 1) then
              if(hnew(m) < topm) topm = hnew(m)
            endif
            if(this%ihc(this%jas(ipos)) == 2) then
              faheight = min(topn, topm) - max(botn, botm)
            else
              faheight = DHALF * ( (topn - botn) + (topm - botm) )
            endif
            fawidth = this%hwva(this%jas(ipos))
            condhfb = this%hydchr(ihfb) * fawidth * faheight
          else
            condhfb = this%hydchr(ihfb)
          end if
        else
          condhfb = this%hydchr(ihfb)
        endif
        ! -- Make hfb corrections for xt3d
        call this%xt3d%xt3d_fhfb(kiter, nodes, nja, njasln, amat, idxglo,      &
          rhs, hnew, n, m, condhfb)
      end do
      !
    else
      !
      ! -- For Newton, the effect of the barrier is included in condsat.
      if(this%inewton == 0) then
        do ihfb = 1, this%nhfb
          ipos = this%idxloc(ihfb)
          aterm = amat(idxglo(ipos))
          n = this%noden(ihfb)
          m = this%nodem(ihfb)
          if(this%ibound(n) == 0 .or. this%ibound(m) == 0) cycle
          if(this%icelltype(n) == 1 .or. this%icelltype(m) == 1) then
            !
            ! -- Calculate hfb conductance
            topn = this%top(n)
            topm = this%top(m)
            botn = this%bot(n)
            botm = this%bot(m)
            if(this%icelltype(n) == 1) then
              if(hnew(n) < topn) topn = hnew(n)
            endif
            if(this%icelltype(m) == 1) then
              if(hnew(m) < topm) topm = hnew(m)
            endif
            if(this%ihc(this%jas(ipos)) == 2) then
              faheight = min(topn, topm) - max(botn, botm)
            else
              faheight = DHALF * ( (topn - botn) + (topm - botm) )
            endif
            if(this%hydchr(ihfb) > DZERO) then
              fawidth = this%hwva(this%jas(ipos))
              condhfb = this%hydchr(ihfb) * fawidth * faheight
              cond = aterm * condhfb / (aterm + condhfb)
            else
              cond = - aterm * this%hydchr(ihfb)
            endif
            !
            ! -- Save cond for budget calculation
            this%condsav(ihfb) = cond
            !
            ! -- Fill row n diag and off diag
            idiag = this%ia(n)
            amat(idxglo(idiag)) = amat(idxglo(idiag)) + aterm - cond
            amat(idxglo(ipos)) = cond
            !
            ! -- Fill row m diag and off diag
            isymcon = this%isym(ipos)
            idiag = this%ia(m)
            amat(idxglo(idiag)) = amat(idxglo(idiag)) + aterm - cond
            amat(idxglo(isymcon)) = cond
            !
          endif
        enddo
      endif
      !
    endif
    !
    ! -- return
    return
  end subroutine hfb_fc

  subroutine hfb_flowja(this, nodes, nja, hnew, flowja)
! ******************************************************************************
! hfb_flowja -- flowja will automatically include the effects of the hfb
!   for confined and newton cases when xt3d is not used.  This method
!   recalculates flowja for the other cases.
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    use ConstantsModule, only: DHALF, DZERO
    ! -- dummy
    class(GwfHfbType) :: this
    integer(I4B),intent(in) :: nodes
    integer(I4B),intent(in) :: nja
    real(DP),intent(inout),dimension(nodes) :: hnew
    real(DP),intent(inout),dimension(nja) :: flowja
    ! -- local
    integer(I4B) :: ihfb, n, m
    integer(I4B) :: ipos
    real(DP) :: qnm
    real(DP) :: cond
    integer(I4B) :: ixt3d
    real(DP) :: condhfb
    real(DP) :: fawidth, faheight
    real(DP) :: topn, topm, botn, botm
! ------------------------------------------------------------------------------
!
    if (associated(this%xt3d%ixt3d)) then
      ixt3d = this%xt3d%ixt3d
    else
      ixt3d = 0
    end if
    !
    if(ixt3d > 0) then
      !
      do ihfb = 1, this%nhfb
        n = min(this%noden(ihfb), this%nodem(ihfb))
        m = max(this%noden(ihfb), this%nodem(ihfb))
        ! -- Skip if either cell is inactive.
        if(this%ibound(n) == 0 .or. this%ibound(m) == 0) cycle
  !!!      if(this%icelltype(n) == 1 .or. this%icelltype(m) == 1) then
        ! -- Compute scale factor for hfb correction
        if(this%hydchr(ihfb) > DZERO) then
          if(this%inewton == 0) then
            ipos = this%idxloc(ihfb)
            topn = this%top(n)
            topm = this%top(m)
            botn = this%bot(n)
            botm = this%bot(m)
            if(this%icelltype(n) == 1) then
              if(hnew(n) < topn) topn = hnew(n)
            endif
            if(this%icelltype(m) == 1) then
              if(hnew(m) < topm) topm = hnew(m)
            endif
            if(this%ihc(this%jas(ipos)) == 2) then
              faheight = min(topn, topm) - max(botn, botm)
            else
              faheight = DHALF * ( (topn - botn) + (topm - botm) )
            endif
            fawidth = this%hwva(this%jas(ipos))
            condhfb = this%hydchr(ihfb) * fawidth * faheight
          else
            condhfb = this%hydchr(ihfb)
          end if
        else
          condhfb = this%hydchr(ihfb)
        endif
        ! -- Make hfb corrections for xt3d
        call this%xt3d%xt3d_flowjahfb(nodes, n, m, nja, hnew, flowja, condhfb)
      end do
      !
    else
      !
      ! -- Recalculate flowja for non-newton unconfined.
      if(this%inewton == 0) then
        do ihfb = 1, this%nhfb
          n = this%noden(ihfb)
          m = this%nodem(ihfb)
          if(this%ibound(n) == 0 .or. this%ibound(m) == 0) cycle
          if(this%icelltype(n) == 1 .or. this%icelltype(m) == 1) then
            ipos = this%dis%con%getjaindex(n, m)
            cond = this%condsav(ihfb)
            qnm = cond * (hnew(m) - hnew(n))
            flowja(ipos) = qnm
            ipos = this%dis%con%getjaindex(m, n)
            flowja(ipos) = -qnm
            !
          endif
        enddo
      endif
      !
    end if
    !
    ! -- return
    return
  end subroutine hfb_flowja

  subroutine hfb_da(this)
! ******************************************************************************
! hfb_da -- Deallocate
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    use MemoryManagerModule, only: mem_deallocate
    ! -- dummy
    class(GwfHfbType) :: this
! ------------------------------------------------------------------------------
    !
    ! -- Strings
    !
    ! -- Scalars
    call mem_deallocate(this%maxhfb)
    call mem_deallocate(this%nhfb)
    !
    ! -- Arrays
    if (this%inunit > 0) then
      call mem_deallocate(this%noden)
      call mem_deallocate(this%nodem)
      call mem_deallocate(this%hydchr)
      call mem_deallocate(this%idxloc)
      call mem_deallocate(this%csatsav)
      call mem_deallocate(this%condsav)
    endif
    !
    ! -- deallocate parent
    call this%NumericalPackageType%da()
    !
    ! -- nullify pointers
    this%xt3d       => null()
    this%inewton    => null()
    this%ibound     => null()
    this%icelltype  => null()
    this%ihc        => null()
    this%ia         => null()
    this%ja         => null()
    this%jas        => null()
    this%isym       => null()
    this%condsat    => null()
    this%top        => null()
    this%bot        => null()
    this%hwva       => null()
    !
    ! -- return
    return
  end subroutine hfb_da

  subroutine allocate_scalars(this)
! ******************************************************************************
! allocate_scalars -- Allocate scalars
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    use MemoryManagerModule, only: mem_allocate
    ! -- dummy
    class(GwfHfbType) :: this
! ------------------------------------------------------------------------------
    !
    ! -- allocate scalars in NumericalPackageType
    call this%NumericalPackageType%allocate_scalars()
    !
    ! -- allocate scalars
    call mem_allocate(this%maxhfb, 'MAXHFB', this%origin)
    call mem_allocate(this%nhfb, 'NHFB', this%origin)
    !
    ! -- initialize
    this%maxhfb = 0
    this%nhfb = 0
    !
    ! -- return
    return
  end subroutine allocate_scalars

  subroutine allocate_arrays(this)
! ******************************************************************************
! allocate_arrays -- Allocate arrays
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    use MemoryManagerModule, only: mem_allocate
    ! -- dummy
    class(GwfHfbType) :: this
    ! -- local
    integer(I4B) :: ihfb
! ------------------------------------------------------------------------------
    !
    call mem_allocate(this%noden, this%maxhfb, 'NODEN', this%origin)
    call mem_allocate(this%nodem, this%maxhfb, 'NODEM', this%origin)
    call mem_allocate(this%hydchr, this%maxhfb, 'HYDCHR', this%origin)
    call mem_allocate(this%idxloc, this%maxhfb, 'IDXLOC', this%origin)
    call mem_allocate(this%csatsav, this%maxhfb, 'CSATSAV', this%origin)
    call mem_allocate(this%condsav, this%maxhfb, 'CONDSAV', this%origin)
    !
    ! -- initialize idxloc to 0
    do ihfb = 1, this%maxhfb
      this%idxloc(ihfb) = 0
    enddo
    !
    ! -- return
    return
  end subroutine allocate_arrays

  subroutine read_options(this)
! ******************************************************************************
! read_options -- read a hfb options block
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    use ConstantsModule, only: LINELENGTH
    use SimModule, only: ustop, store_error, store_error_unit
    ! -- dummy
    class(GwfHfbType) :: this
    ! -- local
    character(len=LINELENGTH) :: errmsg, keyword
    integer(I4B) :: ierr
    logical :: isfound, endOfBlock
! ------------------------------------------------------------------------------
    !
    ! -- get options block
    call this%parser%GetBlock('OPTIONS', isfound, ierr, blockRequired=.false.)
    !
    ! -- parse options block if detected
    if (isfound) then
      write(this%iout,'(1x,a)')'PROCESSING HFB OPTIONS'
      do
        call this%parser%GetNextLine(endOfBlock)
        if (endOfBlock) exit
        call this%parser%GetStringCaps(keyword)
        select case (keyword)
          case ('PRINT_INPUT')
            this%iprpak = 1
            write(this%iout,'(4x,a)') &
              'THE LIST OF HFBS WILL BE PRINTED.'
          case default
            write(errmsg,'(4x,a,a)')'****ERROR. UNKNOWN HFB OPTION: ',         &
                                     trim(keyword)
            call store_error(errmsg)
            call this%parser%StoreErrorUnit()
            call ustop()
        end select
      end do
      write(this%iout,'(1x,a)')'END OF HFB OPTIONS'
    end if
    !
    ! -- return
    return
  end subroutine read_options

  subroutine read_dimensions(this)
! ******************************************************************************
! read_dimensions -- Read the dimensions for this package
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    use ConstantsModule, only: LINELENGTH
    use SimModule, only: ustop, store_error, store_error_unit
    ! -- dummy
    class(GwfHfbType),intent(inout) :: this
    ! -- local
    character(len=LINELENGTH) :: errmsg, keyword
    integer(I4B) :: ierr
    logical :: isfound, endOfBlock
    ! -- format
! ------------------------------------------------------------------------------
    !
    ! -- get dimensions block
    call this%parser%GetBlock('DIMENSIONS', isfound, ierr)
    !
    ! -- parse dimensions block if detected
    if (isfound) then
      write(this%iout,'(/1x,a)')'PROCESSING HFB DIMENSIONS'
      do
        call this%parser%GetNextLine(endOfBlock)
        if (endOfBlock) exit
        call this%parser%GetStringCaps(keyword)
        select case (keyword)
          case ('MAXHFB')
            this%maxhfb = this%parser%GetInteger()
            write(this%iout,'(4x,a,i7)') 'MAXHFB = ', this%maxhfb
          case default
            write(errmsg,'(4x,a,a)') &
              '****ERROR. UNKNOWN HFB DIMENSION: ', &
                                     trim(keyword)
            call store_error(errmsg)
            call this%parser%StoreErrorUnit()
            call ustop()
        end select
      end do
      !
      write(this%iout,'(1x,a)')'END OF HFB DIMENSIONS'
    else
      call store_error('ERROR.  REQUIRED DIMENSIONS BLOCK NOT FOUND.')
      call this%parser%StoreErrorUnit()
      call ustop()
    end if
    !
    ! -- verify dimensions were set
    if(this%maxhfb <= 0) then
      write(errmsg, '(1x,a)') &
        'ERROR.  MAXHFB MUST BE SPECIFIED WITH VALUE GREATER THAN ZERO.'
      call store_error(errmsg)
      call this%parser%StoreErrorUnit()
      call ustop()
    endif
    !
    ! -- return
    return
  end subroutine read_dimensions

  subroutine read_data(this)
! ******************************************************************************
! read_data -- Read hfb period block
!   Data are in form of L, IROW1, ICOL1, IROW2, ICOL2, HYDCHR
!   or for unstructured
!                       N1, N2, HYDCHR
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    use ConstantsModule, only: LINELENGTH
    use SimModule, only: ustop, store_error, count_errors, store_error_unit
    use TdisModule, only: kper
    ! -- dummy
    class(GwfHfbType) :: this
    ! -- local
    character(len=LINELENGTH) :: nodenstr, nodemstr, cellidm, cellidn
    integer(I4B) :: ihfb, nerr
    logical :: endOfBlock
    ! -- formats
    character(len=*), parameter :: fmthfb = "(i10, 2a10, 1(1pg15.6))"
! ------------------------------------------------------------------------------
    !
    write(this%iout,'(//,1x,a)')'READING HFB DATA'
    if(this%iprpak > 0) then
      write(this%iout, '(3a10, 1a15)') 'HFB NUM', 'CELL1', 'CELL2',            &
                                       'HYDCHR'
    endif
    !
    ihfb = 0
    this%nhfb = 0
    readloop: do
      !
      ! -- Check for END of block
      call this%parser%GetNextLine(endOfBlock)
      if (endOfBlock) exit
      !
      ! -- Reset lloc and read noden, nodem, and hydchr
      ihfb = ihfb + 1
      if(ihfb > this%maxhfb) then
        call store_error('MAXHFB not large enough.')
        call this%parser%StoreErrorUnit()
        call ustop()
      endif
      call this%parser%GetCellid(this%dis%ndim, cellidn)
      this%noden(ihfb) = this%dis%noder_from_cellid(cellidn, &
                                       this%parser%iuactive, this%iout)
      call this%parser%GetCellid(this%dis%ndim, cellidm)
      this%nodem(ihfb) = this%dis%noder_from_cellid(cellidm, &
                                       this%parser%iuactive, this%iout)
      this%hydchr(ihfb) = this%parser%GetDouble()
      !
      ! -- Print input if requested
      if(this%iprpak /= 0) then
        call this%dis%noder_to_string(this%noden(ihfb), nodenstr)
        call this%dis%noder_to_string(this%nodem(ihfb), nodemstr)
        write(this%iout, fmthfb) ihfb, trim(adjustl(nodenstr)),                &
                                 trim(adjustl(nodemstr)), this%hydchr(ihfb)
      endif
      !
      this%nhfb = ihfb
    enddo readloop
    !
    ! -- Stop if errors
    nerr = count_errors()
    if(nerr > 0) then
      call store_error('Errors encountered in HFB input file.')
      call this%parser%StoreErrorUnit()
      call ustop()
    endif
    !
    write(this%iout, '(3x,i0,a,i0)') this%nhfb,                                &
          ' HFBs READ FOR STRESS PERIOD ', kper
    call this%check_data()
    write(this%iout, '(1x,a)')'END READING HFB DATA'
    !
    ! -- return
    return
  end subroutine read_data

  subroutine check_data(this)
! ******************************************************************************
! check_data -- Check for hfb's between two unconnected cells and write a
!   warning.  Store ipos in idxloc.
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    use ConstantsModule, only: LINELENGTH
    use SimModule, only: store_error, count_errors, ustop, store_error_unit
    ! -- dummy
    class(GwfHfbType) :: this
    ! -- local
    integer(I4B) :: ihfb, n, m
    integer(I4B) :: ipos
    character(len=LINELENGTH) :: nodenstr, nodemstr
    character(len=LINELENGTH) :: errmsg
    logical :: found
    ! -- formats
    character(len=*), parameter :: fmterr = "(1x, 'Error.  HFB no. ',i0, &
      ' is between two unconnected cells: ', a, ' and ', a)"
! ------------------------------------------------------------------------------
    !
    do ihfb = 1, this%nhfb
      n = this%noden(ihfb)
      m = this%nodem(ihfb)
      found = .false.
      do ipos = this%ia(n)+1, this%ia(n+1)-1
        if(m == this%ja(ipos)) then
          found = .true.
          this%idxloc(ihfb) = ipos
          exit
        endif
      enddo
      if(.not. found) then
        call this%dis%noder_to_string(n, nodenstr)
        call this%dis%noder_to_string(m, nodemstr)
        write(errmsg, fmterr) ihfb, trim(adjustl(nodenstr)),                   &
                                  trim(adjustl(nodemstr))
        call store_error(errmsg)
      endif
    enddo
    !
    ! -- Stop if errors detected
    if(count_errors() > 0) then
      call store_error_unit(this%inunit)
      call ustop()
    endif
    !
    ! -- return
    return
  end subroutine check_data

  subroutine condsat_reset(this)
! ******************************************************************************
! condsat_reset -- Reset condsat to its value prior to being modified by hfb's
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    ! -- dummy
    class(GwfHfbType) :: this
    ! -- local
    integer(I4B) :: ihfb
    integer(I4B) :: ipos
! ------------------------------------------------------------------------------
    !
    do ihfb = 1, this%nhfb
      ipos = this%idxloc(ihfb)
      this%condsat(this%jas(ipos)) = this%csatsav(ihfb)
    enddo
    !
    ! -- return
    return
  end subroutine condsat_reset

  subroutine condsat_modify(this)
! ******************************************************************************
! condsat_modify -- Modify condsat for the following conditions:
!   1.  If Newton is active
!   2.  If icelltype for n and icelltype for m is 0
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- modules
    use ConstantsModule, only: DHALF, DZERO
    ! -- dummy
    class(GwfHfbType) :: this
    ! -- local
    integer(I4B) :: ihfb, n, m
    integer(I4B) :: ipos
    real(DP) :: cond, condhfb
    real(DP) :: fawidth, faheight
    real(DP) :: topn, topm, botn, botm
! ------------------------------------------------------------------------------
    !
    do ihfb = 1, this%nhfb
      ipos = this%idxloc(ihfb)
      cond = this%condsat(this%jas(ipos))
      this%csatsav(ihfb) = cond
      n = this%noden(ihfb)
      m = this%nodem(ihfb)
      if(this%inewton == 1 .or. &
         (this%icelltype(n) == 0 .and. this%icelltype(m) == 0) ) then
        !
        ! -- Calculate hfb conductance
        topn = this%top(n)
        topm = this%top(m)
        botn = this%bot(n)
        botm = this%bot(m)
        if(this%ihc(this%jas(ipos)) == 2) then
          faheight = min(topn, topm) - max(botn, botm)
        else
          faheight = DHALF * ( (topn - botn) + (topm - botm) )
        endif
        if(this%hydchr(ihfb) > DZERO) then
          fawidth = this%hwva(this%jas(ipos))
          condhfb = this%hydchr(ihfb) * fawidth * faheight
          cond = cond * condhfb / (cond + condhfb)
        else
          cond = - cond * this%hydchr(ihfb)
        endif
        this%condsat(this%jas(ipos)) = cond
      endif
    enddo
    !
    ! -- return
    return
  end subroutine condsat_modify

end module GwfHfbModule
