module NumericalModelModule

  use KindModule, only: DP, I4B
  use ConstantsModule, only: LINELENGTH, LENBUDTXT, LENPACKAGENAME
  use BaseModelModule, only: BaseModelType
  use BaseDisModule, only: DisBaseType
  use SparseModule, only: sparsematrix
  use TimeArraySeriesManagerModule, only: TimeArraySeriesManagerType
  use ListModule, only: ListType

  implicit none
  private
  public :: NumericalModelType, AddNumericalModelToList, &
            GetNumericalModelFromList

  type, extends(BaseModelType) :: NumericalModelType
    character(len=LINELENGTH), pointer              :: filename => null()        !input file name
    integer(I4B), pointer                           :: neq      => null()        !number of equations
    integer(I4B), pointer                           :: nja      => null()        !number of connections
    integer(I4B), pointer                           :: moffset  => null()        !offset of this model in the solution
    integer(I4B), pointer                           :: icnvg    => null()        !convergence flag
    integer(I4B), dimension(:), pointer, contiguous :: ia       => null()        !csr row pointer
    integer(I4B), dimension(:), pointer, contiguous :: ja       => null()        !csr columns
    real(DP), dimension(:), pointer, contiguous     :: x        => null()        !dependent variable (head, conc, etc)
    real(DP), dimension(:), pointer, contiguous     :: rhs      => null()        !right-hand side vector
    real(DP), dimension(:), pointer, contiguous     :: cond     => null()        !conductance matrix
    integer(I4B), dimension(:), pointer, contiguous :: idxglo   => null()        !pointer to position in solution matrix
    real(DP), dimension(:), pointer, contiguous     :: xold     => null()        !dependent variable for previous timestep
    real(DP), dimension(:), pointer, contiguous     :: flowja   => null()        !intercell flows
    integer(I4B), dimension(:), pointer, contiguous :: ibound   => null()        !ibound array
    !
    ! -- Derived types
    type(ListType), pointer                         :: bndlist  => null()        !array of boundary packages for this model
    class(DisBaseType), pointer                     :: dis      => null()        !discretization object

  contains
    !
    ! -- Required for all models (override procedures defined in BaseModelType)
    procedure :: model_df
    procedure :: model_ar
    procedure :: model_fp
    procedure :: model_da
    !
    ! -- Methods specific to a numerical model
    procedure :: model_ac
    procedure :: model_mc
    procedure :: model_rp
    procedure :: model_ad
    procedure :: model_cf
    procedure :: model_fc
    procedure :: model_ptcchk
    procedure :: model_ptc
    procedure :: model_nr
    procedure :: model_cc
    procedure :: model_nur
    procedure :: model_cq
    procedure :: model_bd
    procedure :: model_bdcalc
    procedure :: model_bdsave
    procedure :: model_ot
    procedure :: model_bdentry
    !
    ! -- Utility methods
    procedure :: allocate_scalars
    procedure :: allocate_arrays
    procedure :: set_moffset
    procedure :: set_idsoln
    procedure :: set_xptr
    procedure :: set_rhsptr
    procedure :: set_iboundptr
    procedure :: get_nsubtimes
    procedure :: get_mrange
    procedure :: get_mcellid
    procedure :: get_mnodeu
    procedure :: get_iasym
  end type NumericalModelType

  contains
  !
  ! -- Type-bound procedures for a numerical model
  !
  subroutine model_df(this)
    class(NumericalModelType) :: this
  end subroutine model_df

  subroutine model_ac(this, sparse)
    class(NumericalModelType) :: this
    type(sparsematrix), intent(inout) :: sparse
  end subroutine model_ac

  subroutine model_mc(this, iasln, jasln)
    class(NumericalModelType) :: this
    integer(I4B), dimension(:), intent(in) :: iasln
    integer(I4B), dimension(:), intent(in) :: jasln
  end subroutine model_mc

  subroutine model_ar(this)
    class(NumericalModelType) :: this
  end subroutine model_ar

  subroutine model_rp(this)
    class(NumericalModelType) :: this
  end subroutine model_rp

  subroutine model_ad(this, ipicard, isubtime)
    class(NumericalModelType) :: this
    integer(I4B), intent(in) :: ipicard
    integer(I4B), intent(in) :: isubtime
  end subroutine model_ad

  subroutine model_cf(this,kiter)
    class(NumericalModelType) :: this
    integer(I4B),intent(in) :: kiter
  end subroutine model_cf

  subroutine model_fc(this, kiter, amatsln, njasln, inwtflag)
    class(NumericalModelType) :: this
    integer(I4B),intent(in) :: kiter
    real(DP),dimension(njasln),intent(inout) :: amatsln
    integer(I4B),intent(in) :: njasln
    integer(I4B), intent(in) :: inwtflag
  end subroutine model_fc

  subroutine model_ptcchk(this, iptc)
    class(NumericalModelType) :: this
    integer(I4B), intent(inout) :: iptc
    iptc = 0
  end subroutine model_ptcchk

  subroutine model_ptc(this, kiter, neqsln, njasln, &
                       ia, ja, x, rhs, amatsln, iptc, ptcf)
    class(NumericalModelType) :: this
    integer(I4B),intent(in) :: kiter
    integer(I4B), intent(in) :: neqsln
    integer(I4B),intent(in) :: njasln
    integer(I4B), dimension(neqsln+1), intent(in) :: ia
    integer(I4B),dimension(njasln),intent(in) :: ja
    real(DP), dimension(neqsln), intent(in) :: x
    real(DP), dimension(neqsln), intent(in) :: rhs
    real(DP),dimension(njasln),intent(in) :: amatsln
    integer(I4B), intent(inout) :: iptc
    real(DP),intent(inout) :: ptcf
  end subroutine model_ptc

  subroutine model_nr(this, kiter, amatsln, njasln, inwtflag)
    class(NumericalModelType) :: this
    integer(I4B),intent(in) :: kiter
    real(DP),dimension(njasln),intent(inout) :: amatsln
    integer(I4B),intent(in) :: njasln
    integer(I4B), intent(in) :: inwtflag
  end subroutine model_nr

  subroutine model_cc(this, kiter, iend, icnvg, hclose, rclose)
    class(NumericalModelType) :: this
    integer(I4B),intent(in) :: kiter
    integer(I4B),intent(in) :: iend
    integer(I4B),intent(inout) :: icnvg
    real(DP), intent(in) :: hclose
    real(DP), intent(in) :: rclose
  end subroutine model_cc

  subroutine model_nur(this, neqmod, x, xtemp, dx, inewtonur)
    class(NumericalModelType) :: this
    integer(I4B), intent(in) :: neqmod
    real(DP), dimension(neqmod), intent(inout) :: x
    real(DP), dimension(neqmod), intent(in) :: xtemp
    real(DP), dimension(neqmod), intent(inout) :: dx
    integer(I4B), intent(inout) :: inewtonur
  end subroutine model_nur

  subroutine model_cq(this, icnvg, isuppress_output)
    class(NumericalModelType) :: this
    integer(I4B),intent(in) :: icnvg
    integer(I4B), intent(in) :: isuppress_output
  end subroutine model_cq

  subroutine model_bd(this, icnvg, isuppress_output)
    class(NumericalModelType) :: this
    integer(I4B),intent(in) :: icnvg
    integer(I4B), intent(in) :: isuppress_output
  end subroutine model_bd

  subroutine model_bdcalc(this, icnvg)
    class(NumericalModelType) :: this
    integer(I4B),intent(in) :: icnvg
  end subroutine model_bdcalc

  subroutine model_bdsave(this, icnvg)
    class(NumericalModelType) :: this
    integer(I4B),intent(in) :: icnvg
  end subroutine model_bdsave

  subroutine model_ot(this)
    class(NumericalModelType) :: this
  end subroutine model_ot

  subroutine model_bdentry(this, budterm, budtxt, rowlabel)
    class(NumericalModelType) :: this
    real(DP), dimension(:, :), intent(in) :: budterm
    character(len=LENBUDTXT), dimension(:), intent(in) :: budtxt
    character(len=LENPACKAGENAME), intent(in) :: rowlabel
  end subroutine model_bdentry

  subroutine model_fp(this)
    class(NumericalModelType) :: this
  end subroutine model_fp

  subroutine model_da(this)
    ! -- modules
    use MemoryManagerModule, only: mem_deallocate
    class(NumericalModelType) :: this
    !
    ! -- BaseModelType
    call this%BaseModelType%model_da()
    !
    ! -- Scalars
    call mem_deallocate(this%neq)
    call mem_deallocate(this%nja)
    call mem_deallocate(this%icnvg)
    call mem_deallocate(this%moffset)
    deallocate(this%filename)
    !
    ! -- Arrays
    call mem_deallocate(this%xold)
    call mem_deallocate(this%flowja)
    call mem_deallocate(this%idxglo)
    !
    ! -- derived types
    call this%bndlist%Clear()
    deallocate(this%bndlist)
    !
    ! -- nullify pointers
    nullify(this%x)
    nullify(this%rhs)
    nullify(this%ibound)
    !
    ! -- Return
    return
  end subroutine model_da

  subroutine set_moffset(this, moffset)
    class(NumericalModelType) :: this
    integer(I4B), intent(in) :: moffset
    this%moffset = moffset
  end subroutine set_moffset

  subroutine get_mrange(this, mstart, mend)
    class(NumericalModelType) :: this
    integer(I4B), intent(inout) :: mstart
    integer(I4B), intent(inout) :: mend
    mstart = this%moffset + 1
    mend = mstart + this%neq - 1
  end subroutine get_mrange

  subroutine set_idsoln(this, id)
    class(NumericalModelType) :: this
    integer(I4B), intent(in) :: id
    this%idsoln = id
  end subroutine set_idsoln

  subroutine allocate_scalars(this, modelname)
    use MemoryManagerModule, only: mem_allocate
    class(NumericalModelType) :: this
    character(len=*), intent(in)  :: modelname
    !
    ! -- allocate basetype members
    call this%BaseModelType%allocate_scalars(modelname)
    !
    ! -- allocate members from this type
    call mem_allocate(this%neq, 'NEQ', modelname)
    call mem_allocate(this%nja, 'NJA', modelname)
    call mem_allocate(this%icnvg, 'ICNVG', modelname)
    call mem_allocate(this%moffset, 'MOFFSET', modelname)
    allocate(this%filename)
    allocate(this%bndlist)
    !
    this%filename = ''
    this%neq = 0
    this%nja = 0
    this%icnvg = 0
    this%moffset = 0
    !
    ! -- return
    return
  end subroutine allocate_scalars

  subroutine allocate_arrays(this)
    use MemoryManagerModule, only: mem_allocate
    class(NumericalModelType) :: this
    !
    call mem_allocate(this%xold,   this%neq, 'XOLD',   trim(this%name))
    call mem_allocate(this%flowja, this%nja, 'FLOWJA', trim(this%name))
    call mem_allocate(this%idxglo, this%nja, 'IDXGLO', trim(this%name))
    !
    ! -- return
    return
  end subroutine allocate_arrays

  subroutine set_xptr(this, xsln)
    class(NumericalModelType) :: this
    real(DP), dimension(:), pointer, contiguous, intent(in) :: xsln
    this%x => xsln(this%moffset + 1:this%moffset + this%neq)
  end subroutine set_xptr

  subroutine set_rhsptr(this, rhssln)
    class(NumericalModelType) :: this
    real(DP), dimension(:), pointer, contiguous, intent(in) :: rhssln
    this%rhs => rhssln(this%moffset + 1:this%moffset + this%neq)
  end subroutine set_rhsptr

  subroutine set_iboundptr(this, iboundsln)
    class(NumericalModelType) :: this
    integer(I4B), dimension(:), pointer, contiguous, intent(in) :: iboundsln
    this%ibound => iboundsln(this%moffset + 1:this%moffset + this%neq)
  end subroutine set_iboundptr

  function get_nsubtimes(this) result(nsubtimes)
    integer(I4B) :: nsubtimes
    class(NumericalModelType) :: this
    nsubtimes = 1
    return
  end function get_nsubtimes

  subroutine get_mcellid(this, node, mcellid)
    use BndModule, only: BndType, GetBndFromList
    class(NumericalModelType) :: this
    integer(I4B), intent(in) :: node
    character(len=*), intent(inout) :: mcellid
    ! -- local
    character(len=20) :: cellid
    integer(I4B) :: ip, ipaknode, istart, istop
    class(BndType), pointer :: packobj
    
    if(node <= this%dis%nodes) then
      call this%dis%noder_to_string(node, cellid)
    else
      cellid = '***ERROR***'
      ipaknode = node - this%dis%nodes
      istart = 1
      do ip = 1, this%bndlist%Count()
        packobj => GetBndFromList(this%bndlist, ip)
        if(packobj%npakeq == 0) cycle
        istop = istart + packobj%npakeq - 1
        if(istart <= ipaknode .and. ipaknode <= istop) then
          write(cellid, '(a, a, a, i0, a, i0, a)') '(',                        &
            trim(packobj%filtyp), '_',                                         &
            packobj%ibcnum, '-', ipaknode - packobj%ioffset, ')'
          exit
        endif
        istart = istop + 1
      enddo
    endif
    write(mcellid, '(i0, a, a, a, a)') this%id, '_', this%macronym, '-',       &
      trim(adjustl(cellid))
    return
  end subroutine get_mcellid

  subroutine get_mnodeu(this, node, nodeu)
    use BndModule, only: BndType, GetBndFromList
    class(NumericalModelType) :: this
    integer(I4B), intent(in) :: node
    integer(I4B), intent(inout) :: nodeu
    ! -- local
    integer(I4B) :: ip, ipaknode, istart, istop
    class(BndType), pointer :: packobj
    
    if(node <= this%dis%nodes) then
      nodeu = this%dis%get_nodeuser(node)
    else
      nodeu = -(node - this%dis%nodes)
    endif
    return
  end subroutine get_mnodeu
  
  function get_iasym(this) result (iasym)
    class(NumericalModelType) :: this
    integer(I4B) :: iasym
    iasym = 0
  end function get_iasym

  function CastAsNumericalModelClass(obj) result (res)
    implicit none
    class(*), pointer, intent(inout) :: obj
    class(NumericalModelType), pointer :: res
    !
    res => null()
    if (.not. associated(obj)) return
    !
    select type (obj)
    class is (NumericalModelType)
      res => obj
    end select
    return
  end function CastAsNumericalModelClass

  subroutine AddNumericalModelToList(list, model)
    implicit none
    ! -- dummy
    type(ListType),             intent(inout) :: list
    class(NumericalModelType), pointer, intent(inout) :: model
    ! -- local
    class(*), pointer :: obj
    !
    obj => model
    call list%Add(obj)
    !
    return
  end subroutine AddNumericalModelToList
  
  function GetNumericalModelFromList(list, idx) result (res)
    implicit none
    ! -- dummy
    type(ListType),           intent(inout) :: list
    integer(I4B),                  intent(in)    :: idx
    class(NumericalModelType), pointer       :: res
    ! -- local
    class(*), pointer :: obj
    !
    obj => list%GetItem(idx)
    res => CastAsNumericalModelClass(obj)
    !
    return
  end function GetNumericalModelFromList

end module NumericalModelModule
