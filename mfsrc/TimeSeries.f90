module TimeSeriesModule

  use KindModule, only: DP, I4B
  use BlockParserModule,      only: BlockParserType
  use ConstantsModule,        only: LINELENGTH, UNDEFINED, STEPWISE, LINEAR, &
                                    LINEAREND, LENTIMESERIESNAME, LENHUGELINE, &
                                    DZERO, DONE, DNODATA
  use GenericUtilities,       only: IS_SAME
  use InputOutputModule,      only: GetUnit, openfile, ParseLine, upcase
  use ListModule,             only: ListType, ListNodeType
  use SimModule,              only: count_errors, store_error, &
                                    store_error_unit, ustop
  use TimeSeriesRecordModule, only: TimeSeriesRecordType, &
                                    ConstructTimeSeriesRecord, &
                                    CastAsTimeSeriesRecordType, &
                                    AddTimeSeriesRecordToList

  private
  public :: TimeSeriesType, TimeSeriesFileType, ConstructTimeSeriesFile, &
            TimeSeriesContainerType, AddTimeSeriesFileToList, &
            GetTimeSeriesFileFromList, CastAsTimeSeriesFileClass, &
            SameTimeSeries

  type TimeSeriesType
    ! -- Public members
    integer(I4B), public :: iMethod = UNDEFINED
    character(len=LENTIMESERIESNAME), public :: Name = ''
    ! -- Private members
    real(DP), private :: sfac = DONE
    logical, public :: autoDeallocate = .true.
    type(ListType), pointer, private :: list => null()
    class(TimeSeriesFileType), pointer, private :: tsfile => null()
  contains
    ! -- Public procedures
    procedure, public :: AddTimeSeriesRecord
    procedure, public :: Clear
    procedure, public :: FindLatestTime
    procedure, public :: get_surrounding_records
    procedure, public :: get_surrounding_nodes
    procedure, public :: GetCurrentTimeSeriesRecord
    procedure, public :: GetNextTimeSeriesRecord
    procedure, public :: GetPreviousTimeSeriesRecord
    procedure, public :: GetTimeSeriesRecord
    procedure, public :: GetValue
    procedure, public :: InitializeTimeSeries => initialize_time_series
    procedure, public :: InsertTsr
    procedure, public :: Reset
    ! -- Private procedures
    procedure, private :: da => ts_da
    procedure, private :: get_average_value
    procedure, private :: get_integrated_value
    procedure, private :: get_latest_preceding_node
    procedure, private :: get_value_at_time
    procedure, private :: initialize_time_series
    procedure, private :: read_next_record
  end type TimeSeriesType

  type TimeSeriesFileType
    ! -- Private members
    integer(I4B), public :: inunit = 0
    integer(I4B), public :: iout = 0
    integer(I4B), public :: nTimeSeries = 0
    character(len=LINELENGTH), public :: datafile = ''
    type(TimeSeriesType), dimension(:), pointer, contiguous, public :: timeSeries => null()
    type(BlockParserType), pointer, public :: parser
  contains
    ! -- Public procedures
    procedure, public :: Count
    procedure, public :: Initializetsfile
    procedure, public :: GetTimeSeries
    procedure, public :: da => tsf_da
    ! -- Private procedures
    procedure, private :: read_tsfile_line
  end type TimeSeriesFileType

  type TimeSeriesContainerType
    ! -- Public members
    type(TimeSeriesType), pointer, public :: timeSeries => null()
  end type TimeSeriesContainerType

contains

  ! -- non-type-bound procedures

  subroutine ConstructTimeSeriesFile(newTimeSeriesFile)
! ******************************************************************************
! ConstructTimeSeriesFile -- construct ts tsfile
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    type(TimeSeriesFileType), pointer, intent(inout) :: newTimeSeriesFile
! ------------------------------------------------------------------------------
    !
    allocate(newTimeSeriesFile)
    allocate(newTimeSeriesFile%parser)
    return
  end subroutine ConstructTimeSeriesFile

  function CastAsTimeSeriesFileType(obj) result(res)
! ******************************************************************************
! CastAsTimeSeriesFileType -- Cast an unlimited polymorphic object as 
!   class(TimeSeriesFileType)
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(*), pointer, intent(inout) :: obj
    ! -- return
    type(TimeSeriesFileType), pointer :: res
! ------------------------------------------------------------------------------
    !
    res => null()
    if (.not. associated(obj)) return
    !
    select type (obj)
    type is (TimeSeriesFileType)
      res => obj
    end select
    return
  end function CastAsTimeSeriesFileType

  function CastAsTimeSeriesFileClass(obj) result(res)
! ******************************************************************************
! CastAsTimeSeriesFileClass -- Cast an unlimited polymorphic object as 
!   class(TimeSeriesFileType)
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(*), pointer, intent(inout) :: obj
    ! -- return
    type(TimeSeriesFileType), pointer :: res
! ------------------------------------------------------------------------------
    !
    res => null()
    if (.not. associated(obj)) return
    !
    select type (obj)
    class is (TimeSeriesFileType)
      res => obj
    end select
    return
  end function CastAsTimeSeriesFileClass

  subroutine AddTimeSeriesFileToList(list, tsfile)
! ******************************************************************************
! AddTimeSeriesFileToList -- add to list
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    type(ListType),                      intent(inout) :: list
    class(TimeSeriesFileType), pointer, intent(inout) :: tsfile
    ! -- local
    class(*), pointer :: obj
! ------------------------------------------------------------------------------
    !
    obj => tsfile
    call list%Add(obj)
    !
    return
  end subroutine AddTimeSeriesFileToList

  function GetTimeSeriesFileFromList(list, idx) result (res)
! ******************************************************************************
! GetTimeSeriesFileFromList -- get from list
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    type(ListType),      intent(inout) :: list
    integer(I4B),             intent(in)    :: idx
    type(TimeSeriesFileType), pointer :: res
    ! -- local
    class(*), pointer :: obj
! ------------------------------------------------------------------------------
    !
    obj => list%GetItem(idx)
    res => CastAsTimeSeriesFileType(obj)
    !
    if (.not. associated(res)) then
      res => CastAsTimeSeriesFileClass(obj)
    endif
    !
    return
  end function GetTimeSeriesFileFromList

  function SameTimeSeries(ts1, ts2) result (same)
! ******************************************************************************
! SameTimeSeries -- Compare two time series; if they are identical, return true.
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    type(TimeSeriesType), intent(in) :: ts1
    type(TimeSeriesType), intent(in) :: ts2
    logical :: same
    ! -- local
    integer :: i, n1, n2
    type(TimeSeriesRecordType), pointer :: tsr1, tsr2
! ------------------------------------------------------------------------------
    !
    same = .false.
    n1 = ts1%list%Count()
    n2 = ts2%list%Count()
    if (n1 /= n2) return
    !
    call ts1%Reset()
    call ts2%Reset()
    !
    do i=1,n1
      tsr1 => ts1%GetNextTimeSeriesRecord()
      tsr2 => ts2%GetNextTimeSeriesRecord()
      if (tsr1%tsrTime /= tsr2%tsrTime) return
      if (tsr1%tsrValue /= tsr2%tsrValue) return
    enddo
    !
    same = .true.
    !
    return
  end function SameTimeSeries

  ! Type-bound procedures of TimeSeriesType

  function GetValue(this, time0, time1)
! ******************************************************************************
! GetValue -- get ts value
!    If iMethod is STEPWISE or LINEAR:
!        Return a time-weighted average value for a specified time span.
!    If iMethod is LINEAREND:
!        Return value at time1. Time0 argument is ignored.
!    Units: (ts-value-unit)
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- return
    real(DP) :: GetValue
    ! -- dummy
    class(TimeSeriesType), intent(inout) :: this
    real(DP),      intent(in)    :: time0
    real(DP),      intent(in)    :: time1
! ------------------------------------------------------------------------------
    !
    select case (this%iMethod)
    case (STEPWISE, LINEAR)
      GetValue = this%get_average_value(time0, time1)
    case (LINEAREND)
      GetValue =  this%get_value_at_time(time1)
    end select
    !
    return
  end function GetValue

  subroutine initialize_time_series(this, tsfile, name, autoDeallocate)
! ******************************************************************************
! initialize_time_series -- initialize time series
!    Open time-series file and read options and first time-series record.
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType), intent(inout) :: this
    class(TimeSeriesFileType), target   :: tsfile
    character(len=*),      intent(in)    :: name
    logical, intent(in), optional        :: autoDeallocate
    ! -- local
    character(len=LINELENGTH) :: ermsg
    character(len=LENTIMESERIESNAME) :: tsNameTemp
! ------------------------------------------------------------------------------
    !
    ! -- Assign the time-series tsfile, name, and autoDeallocate
    this%tsfile => tsfile
    ! Store time-series name as all caps
    tsNameTemp = name
    call UPCASE(tsNameTemp)
    this%Name = tsNameTemp
    !
    this%iMethod = UNDEFINED
    !
    if (present(autoDeallocate)) this%autoDeallocate = autoDeallocate
    !
    ! -- allocate the list
    allocate(this%list)
    !
    ! -- ensure that NAME has been specified
    if (this%Name == '') then
      ermsg = 'Error: Name not specified for time series.'
      call store_error(ermsg)
      call ustop()
    endif
    !
    return
  end subroutine initialize_time_series

  subroutine get_surrounding_records(this, time, tsrecEarlier, tsrecLater)
! ******************************************************************************
! get_surrounding_records -- get surrounding records
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType), intent(inout) :: this
    real(DP),      intent(in)    :: time
    type(TimeSeriesRecordType), pointer, intent(inout) :: tsrecEarlier
    type(TimeSeriesRecordType), pointer, intent(inout) :: tsrecLater
    ! -- local
    real(DP) :: time0, time1
    type(ListNodeType), pointer :: currNode => null()
    type(ListNodeType), pointer :: tsNode0 => null()
    type(ListNodeType), pointer :: tsNode1 => null()
    type(TimeSeriesRecordType), pointer :: tsr => null(), tsrec0 => null()
    type(TimeSeriesRecordType), pointer :: tsrec1 => null()
    class(*),                   pointer :: obj => null()
! ------------------------------------------------------------------------------
    !
    tsrecEarlier => null()
    tsrecLater => null()
    !
    if (associated(this%list%firstNode)) then
      currNode => this%list%firstNode
    endif
    !
    ! -- If the next node is earlier than time of interest, advance along
    !    linked list until the next node is later than time of interest.
    do
      if (associated(currNode)) then
        if (associated(currNode%nextNode)) then
          obj => currNode%nextNode%GetItem()
          tsr => CastAsTimeSeriesRecordType(obj)
          if (tsr%tsrTime < time .and. .not. IS_SAME(tsr%tsrTime, time)) then
            currNode => currNode%nextNode
          else
            exit
          endif
        else
          ! -- read another record
          if (.not. this%read_next_record()) exit
        endif
      else
        exit
      endif
    enddo
    !
    if (associated(currNode)) then
      !
      ! -- find earlier record
      tsNode0 => currNode
      obj => tsNode0%GetItem()
      tsrec0 => CastAsTimeSeriesRecordType(obj)
      time0 = tsrec0%tsrTime
      do while (time0 > time)
        if (associated(tsNode0%prevNode)) then
          tsNode0 => tsNode0%prevNode
          obj => tsNode0%GetItem()
          tsrec0 => CastAsTimeSeriesRecordType(obj)
          time0 = tsrec0%tsrTime
        else
          exit
        endif
      enddo
      !
      ! -- find later record
      tsNode1 => currNode
      obj => tsNode1%GetItem()
      tsrec1 => CastAsTimeSeriesRecordType(obj)
      time1 = tsrec1%tsrTime
      do while (time1 < time .and. .not. IS_SAME(time1, time))
        if (associated(tsNode1%nextNode)) then
          tsNode1 => tsNode1%nextNode
          obj => tsNode1%GetItem()
          tsrec1 => CastAsTimeSeriesRecordType(obj)
          time1 = tsrec1%tsrTime
        else
          ! -- get next record
          if (.not. this%read_next_record()) then
            ! -- end of file reached, so exit loop
            exit
          endif
        endif
      enddo
      !
    endif
    !
    if (time0 < time .or. IS_SAME(time0, time)) tsrecEarlier => tsrec0
    if (time1 > time .or. IS_SAME(time1, time)) tsrecLater => tsrec1
    !
    return
  end subroutine get_surrounding_records

  subroutine get_surrounding_nodes(this, time, nodeEarlier, nodeLater)
! ******************************************************************************
! get_surrounding_nodes -- get surrounding nodes
!   This subroutine is for working with time series already entirely stored
!   in memory -- it does not read data from a file.
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType),       intent(inout) :: this
    real(DP),                    intent(in)    :: time
    type(ListNodeType), pointer, intent(inout) :: nodeEarlier
    type(ListNodeType), pointer, intent(inout) :: nodeLater
    ! -- local
    real(DP) :: time0, time1
    type(ListNodeType), pointer :: currNode => null()
    type(ListNodeType), pointer :: tsNode0 => null()
    type(ListNodeType), pointer :: tsNode1 => null()
    type(TimeSeriesRecordType), pointer :: tsr => null(), tsrec0 => null()
    type(TimeSeriesRecordType), pointer :: tsrec1 => null()
    type(TimeSeriesRecordType), pointer :: tsrecEarlier
    type(TimeSeriesRecordType), pointer :: tsrecLater
    class(*),                   pointer :: obj => null()
! ------------------------------------------------------------------------------
    !
    tsrecEarlier => null()
    tsrecLater => null()
    nodeEarlier => null()
    nodeLater  => null()
    !
    if (associated(this%list%firstNode)) then
      currNode => this%list%firstNode
    endif
    !
    ! -- If the next node is earlier than time of interest, advance along
    !    linked list until the next node is later than time of interest.
    do
      if (associated(currNode)) then
        if (associated(currNode%nextNode)) then
          obj => currNode%nextNode%GetItem()
          tsr => CastAsTimeSeriesRecordType(obj)
          if (tsr%tsrTime < time .and. .not. IS_SAME(tsr%tsrTime, time)) then
            currNode => currNode%nextNode
          else
            exit
          endif
        else
          exit
        endif
      else
        exit
      endif
    enddo
    !
    if (associated(currNode)) then
      !
      ! -- find earlier record
      tsNode0 => currNode
      obj => tsNode0%GetItem()
      tsrec0 => CastAsTimeSeriesRecordType(obj)
      time0 = tsrec0%tsrTime
      do while (time0 > time)
        if (associated(tsNode0%prevNode)) then
          tsNode0 => tsNode0%prevNode
          obj => tsNode0%GetItem()
          tsrec0 => CastAsTimeSeriesRecordType(obj)
          time0 = tsrec0%tsrTime
        else
          exit
        endif
      enddo
      !
      ! -- find later record
      tsNode1 => currNode
      obj => tsNode1%GetItem()
      tsrec1 => CastAsTimeSeriesRecordType(obj)
      time1 = tsrec1%tsrTime
      do while (time1 < time .and. .not. IS_SAME(time1, time))
        if (associated(tsNode1%nextNode)) then
          tsNode1 => tsNode1%nextNode
          obj => tsNode1%GetItem()
          tsrec1 => CastAsTimeSeriesRecordType(obj)
          time1 = tsrec1%tsrTime
        else
          exit
        endif
      enddo
      !
    endif
    !
    if (time0 < time .or. IS_SAME(time0, time)) then
      tsrecEarlier => tsrec0
      nodeEarlier => tsNode0
    endif
    if (time1 > time .or. IS_SAME(time1, time)) then
      tsrecLater => tsrec1
      nodeLater => tsNode1
    endif
    !
    return
  end subroutine get_surrounding_nodes

  logical function read_next_record(this)
! ******************************************************************************
! read_next_record -- read next record
!   Read next time-series record from input file.
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType), intent(inout) :: this
    ! -- local
! ------------------------------------------------------------------------------
    !
    read_next_record = this%tsfile%read_tsfile_line()
    return
    !
  end function read_next_record

  function get_value_at_time(this, time)
! ******************************************************************************
! get_value_at_time -- get value for a time
!   Return a value for a specified time, same units as time-series values.
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- return
    real(DP) :: get_value_at_time
    ! -- dummy
    class(TimeSeriesType), intent(inout) :: this
    real(DP),      intent(in)    :: time ! time of interest
    ! -- local
    integer(I4B) :: ierr
    real(DP) :: ratio, time0, time1, timediff, timediffi, val0, val1, &
                        valdiff
    character(len=LINELENGTH) :: errmsg
    type(TimeSeriesRecordType), pointer :: tsrEarlier => null()
    type(TimeSeriesRecordType), pointer :: tsrLater => null()
    ! -- formats
    10 format('Error getting value at time ',g10.3,' for time series "',a,'"')
! ------------------------------------------------------------------------------
    !
    ierr = 0
    call this%get_surrounding_records(time,tsrEarlier,tsrLater)
    if (associated(tsrEarlier)) then
      if (associated(tsrLater)) then
        ! -- values are available for both earlier and later times
        if (this%iMethod == STEPWISE) then
          get_value_at_time =  tsrEarlier%tsrValue
        elseif (this%iMethod == LINEAR .or. this%iMethod == LINEAREND) then
          ! -- For get_value_at_time, result is the same for either
          !    linear method.
          ! -- Perform linear interpolation.
          time0 = tsrEarlier%tsrTime
          time1 = tsrLater%tsrtime
          timediff = time1 - time0
          timediffi = time - time0
          if (timediff>0) then
            ratio = timediffi/timediff
          else
            ! -- should not happen if TS does not contain duplicate times
            ratio = 0.5d0
          endif
          val0 = tsrEarlier%tsrValue
          val1 = tsrLater%tsrValue
          valdiff = val1 - val0
          get_value_at_time = val0 + (ratio*valdiff)
        else
          ierr = 1
        endif
      else
        if (IS_SAME(tsrEarlier%tsrTime, time)) then
          get_value_at_time = tsrEarlier%tsrValue
        else
          ! -- Only earlier time is available, and it is not time of interest;
          !    however, if method is STEPWISE, use value for earlier time.
          if (this%iMethod == STEPWISE) then
            get_value_at_time =  tsrEarlier%tsrValue
          else
            ierr = 1
          endif
        endif
      endif
    else
      if (associated(tsrLater)) then
        if (IS_SAME(tsrLater%tsrTime, time)) then
          get_value_at_time = tsrLater%tsrValue
        else
          ! -- only later time is available, and it is not time of interest
          ierr = 1
        endif
      else
        ! -- Neither earlier nor later time is available.
        !    This should never happen!
        ierr = 1
      endif
    endif
    !
    if (ierr > 0) then
      write(errmsg,10)time,trim(this%Name)
      call store_error(errmsg)
      call ustop()
    endif
    !
    return
  end function get_value_at_time

  function get_integrated_value(this, time0, time1)
! ******************************************************************************
! get_integrated_value -- get integrated value
!   Return an integrated value for a specified time span.
!    Units: (ts-value-unit)*time
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- return
    real(DP) :: get_integrated_value
    ! -- dummy
    class(TimeSeriesType), intent(inout) :: this
    real(DP),      intent(in)    :: time0
    real(DP),      intent(in)    :: time1
    ! -- local
    real(DP) :: area, currTime, nextTime, ratio0, ratio1, t0, t01, t1, &
                        timediff, value, value0, value1, valuediff
    logical :: ldone
    character(len=LINELENGTH) :: errmsg
    type(ListNodeType), pointer :: tslNodePreceding => null()
    type(ListNodeType), pointer :: currNode => null(), nextNode => null()
    type(TimeSeriesRecordType), pointer :: currRecord => null()
    type(TimeSeriesRecordType), pointer :: nextRecord => null()
    class(*), pointer :: currObj => null(), nextObj => null()
    ! -- formats
    10 format('Error encountered while performing integration', &
        ' for time series "',a,'" for time interval: ',g12.5,' to ',g12.5)
! ------------------------------------------------------------------------------
    !
    value = DZERO
    ldone = .false.
    t1 = -DONE
    call this%get_latest_preceding_node(time0, tslNodePreceding)
    if (associated(tslNodePreceding)) then
      currNode => tslNodePreceding
      do while (.not. ldone)
        currObj => currNode%GetItem()
        currRecord => CastAsTimeSeriesRecordType(currObj)
        currTime = currRecord%tsrTime
        if (IS_SAME(currTime, time1)) then
          ! Current node time = time1 so should be ldone
          ldone = .true.
        elseif (currTime < time1) then
          if (.not. associated(currNode%nextNode)) then
            ! -- try to read the next record
            if (.not. this%read_next_record()) then
              write(errmsg,10)trim(this%Name),time0,time1
              call store_error(errmsg)
              call ustop()
            endif
          endif
          if (associated(currNode%nextNode)) then
            nextNode => currNode%nextNode
            nextObj => nextNode%GetItem()
            nextRecord => CastAsTimeSeriesRecordType(nextObj)
            nextTime = nextRecord%tsrTime
            ! -- determine lower and upper limits of time span of interest
            !    within current interval
            if (currTime > time0 .or. IS_SAME(currTime, time0)) then
              t0 = currTime
            else
              t0 = time0
            endif
            if (nextTime < time1 .or. IS_SAME(nextTime, time1)) then
              t1 = nextTime
            else
              t1 = time1
            endif
            ! -- find area of rectangle or trapezoid delimited by t0 and t1
            t01 = t1 - t0
            select case (this%iMethod)
            case (STEPWISE)
              ! -- compute area of a rectangle
              value0 = currRecord%tsrValue
              area = value0 * t01
            case (LINEAR, LINEAREND)
              ! -- compute area of a trapezoid
              timediff = nextTime - currTime
              ratio0 = (t0 - currTime) / timediff
              ratio1 = (t1 - currTime) / timediff
              valuediff = nextRecord%tsrValue - currRecord%tsrValue
              value0 = currRecord%tsrValue + ratio0 * valuediff
              value1 = currRecord%tsrValue + ratio1 * valuediff
              if (this%iMethod == LINEAR) then
                area = 0.5d0 * t01 * (value0 + value1)
              elseif (this%iMethod == LINEAREND) then
                area = DZERO
                value = value1
              endif
            end select
            ! -- add area to integrated value
            value = value + area
          endif
        endif
        !
        ! -- Are we done yet?
        if (t1 > time1) then
          ldone = .true.
        elseif (IS_SAME(t1, time1)) then
          ldone = .true.
        else
          ! -- We are not done yet
          if (.not. associated(currNode%nextNode)) then
            ! -- Not done and no more data, so try to read the next record
            if (.not. this%read_next_record()) then
              write(errmsg,10)trim(this%Name),time0,time1
              call store_error(errmsg)
              call ustop()
            endif
          elseif (associated(currNode%nextNode)) then
            currNode => currNode%nextNode
          endif
        endif
      enddo
    endif
    !
    get_integrated_value = value
    if (this%autoDeallocate) then
      if (associated(tslNodePreceding)) then
        if (associated(tslNodePreceding%prevNode))then
          call this%list%DeallocateBackward(tslNodePreceding%prevNode)
        endif
      endif
    endif
    return
  end function get_integrated_value

  function get_average_value(this, time0, time1)
! ******************************************************************************
! get_average_value -- get average value
!   Return a time-weighted average value for a specified time span.
!    Units: (ts-value-unit)
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- return
    real(DP) :: get_average_value
    ! -- dummy
    class(TimeSeriesType), intent(inout) :: this
    real(DP),      intent(in)    :: time0
    real(DP),      intent(in)    :: time1
    ! -- local
    real(DP) :: timediff, value, valueIntegrated
! ------------------------------------------------------------------------------
    !
    timediff = time1 - time0
    if (timediff > 0) then
      valueIntegrated = this%get_integrated_value(time0, time1)
      if (this%iMethod == LINEAREND) then
        value = valueIntegrated
      else
        value = valueIntegrated / timediff
      endif
    else
      ! -- time0 and time1 are the same
      value = this%get_value_at_time(time0)
    endif
    get_average_value = value
    !
    return
  end function get_average_value

  subroutine get_latest_preceding_node(this, time, tslNode)
! ******************************************************************************
! get_latest_preceding_node -- get latest prececing node
!   Return pointer to ListNodeType object for the node
!   representing the latest preceding time in the time series
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType),      intent(inout) :: this
    real(DP),            intent(in)    :: time
    type(ListNodeType), pointer, intent(inout) :: tslNode
    ! -- local
    real(DP) :: time0
    type(ListNodeType), pointer :: currNode => null()
    type(ListNodeType), pointer :: tsNode0 => null()
    type(TimeSeriesRecordType), pointer :: tsr => null()
    type(TimeSeriesRecordType), pointer :: tsrec0 => null()
    class(*),                   pointer :: obj => null()
! ------------------------------------------------------------------------------
    !
    tslNode => null()
    if (associated(this%list%firstNode)) then
      currNode => this%list%firstNode
    else
      call store_error('probable programming error in get_latest_preceding_node')
      call ustop()
    endif
    !
    ! -- If the next node is earlier than time of interest, advance along
    !    linked list until the next node is later than time of interest.
    do
      if (associated(currNode)) then
        if (associated(currNode%nextNode)) then
          obj => currNode%nextNode%GetItem()
          tsr => CastAsTimeSeriesRecordType(obj)
          if (tsr%tsrTime < time .or. IS_SAME(tsr%tsrTime, time)) then
            currNode => currNode%nextNode
          else
            exit
          endif
        else
          ! -- read another record
          if (.not. this%read_next_record()) exit
        endif
      else
        exit
      endif
    enddo
    !
    if (associated(currNode)) then
      !
      ! -- find earlier record
      tsNode0 => currNode
      obj => tsNode0%GetItem()
      tsrec0 => CastAsTimeSeriesRecordType(obj)
      time0 = tsrec0%tsrTime
      do while (time0 > time)
        if (associated(tsNode0%prevNode)) then
          tsNode0 => tsNode0%prevNode
          obj => tsNode0%GetItem()
          tsrec0 => CastAsTimeSeriesRecordType(obj)
          time0 = tsrec0%tsrTime
        else
          exit
        endif
      enddo
    endif
    !
    if (time0 < time .or. IS_SAME(time0, time)) tslNode => tsNode0
    !
    return
  end subroutine get_latest_preceding_node

  subroutine ts_da(this)
! ******************************************************************************
! ts_da -- deallocate
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType), intent(inout) :: this
! ------------------------------------------------------------------------------
    !
    if (associated(this%list)) then
      call this%list%Clear(.true.)
      deallocate(this%list)
    endif
    !
    return
  end subroutine ts_da

  subroutine AddTimeSeriesRecord(this, tsr)
! ******************************************************************************
! AddTimeSeriesRecord -- add ts record
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType) :: this
    type(TimeSeriesRecordType), pointer, intent(inout) :: tsr
    ! -- local
    class(*), pointer :: obj
! ------------------------------------------------------------------------------
    !
    obj => tsr
    call this%list%Add(obj)
    !
    return
  end subroutine AddTimeSeriesRecord

  function GetCurrentTimeSeriesRecord(this) result (res)
! ******************************************************************************
! GetCurrentTimeSeriesRecord -- get current ts record
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType) :: this
    ! result
    type(TimeSeriesRecordType), pointer :: res
    ! -- local
    class(*), pointer :: obj
! ------------------------------------------------------------------------------
    !
    obj => null()
    res => null()
    obj => this%list%GetItem()
    if (associated(obj)) then
      res => CastAsTimeSeriesRecordType(obj)
    endif
    !
    return
  end function GetCurrentTimeSeriesRecord

  function GetPreviousTimeSeriesRecord(this) result (res)
! ******************************************************************************
! GetPreviousTimeSeriesRecord -- get previous ts record
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType) :: this
    ! result
    type(TimeSeriesRecordType), pointer :: res
    ! -- local
    class(*), pointer :: obj
! ------------------------------------------------------------------------------
    !
    obj => null()
    res => null()
    obj => this%list%GetPreviousItem()
    if (associated(obj)) then
      res => CastAsTimeSeriesRecordType(obj)
    endif
    !
    return
  end function GetPreviousTimeSeriesRecord

  function GetNextTimeSeriesRecord(this) result (res)
! ******************************************************************************
! GetNextTimeSeriesRecord -- get next ts record
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType) :: this
    ! result
    type(TimeSeriesRecordType), pointer :: res
    ! -- local
    class(*), pointer :: obj
! ------------------------------------------------------------------------------
    !
    obj => null()
    res => null()
    obj => this%list%GetNextItem()
    if (associated(obj)) then
      res => CastAsTimeSeriesRecordType(obj)
    endif
    !
    return
  end function GetNextTimeSeriesRecord

  function GetTimeSeriesRecord(this, time, epsi)  result (res)
! ******************************************************************************
! GetTimeSeriesRecord -- get ts record
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType) :: this
    double precision, intent(in) :: time
    double precision, intent(in) :: epsi
    ! result
    type(TimeSeriesRecordType), pointer :: res
    ! -- local
    type(TimeSeriesRecordType), pointer :: tsr
! ------------------------------------------------------------------------------
    !
    call this%list%Reset()
    res => null()
    do
      tsr => this%GetNextTimeSeriesRecord()
      if (associated(tsr)) then
        if (IS_SAME(tsr%tsrTime, time)) then
          res => tsr
          exit
        endif
        if (tsr%tsrTime > time) exit
      else
        exit
      endif
    enddo
    !
    return
  end function GetTimeSeriesRecord

  subroutine Reset(this)
! ******************************************************************************
! Reset -- reset
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType) :: this
! ------------------------------------------------------------------------------
    !
    call this%list%Reset()
    !
    return
  end subroutine Reset

  subroutine InsertTsr(this, tsr)
! ******************************************************************************
! InsertTsr -- insert ts record
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType),               intent(inout) :: this
    type(TimeSeriesRecordType), pointer, intent(inout) :: tsr
    ! -- local
    double precision :: badtime, time, time0, time1
    type(TimeSeriesRecordType), pointer :: tsrEarlier, tsrLater
    type(ListNodeType), pointer :: nodeEarlier, nodeLater
    class(*), pointer :: obj
! ------------------------------------------------------------------------------
    !
    badtime = -9.0d30
    time0 = badtime
    time1 = badtime
    time = tsr%tsrTime
    call this%get_surrounding_nodes(time, nodeEarlier, nodeLater)
    !
    if (associated(nodeEarlier)) then
      obj => nodeEarlier%GetItem()
      tsrEarlier => CastAsTimeSeriesRecordType(obj)
      if (associated(tsrEarlier)) then
        time0 = tsrEarlier%tsrTime
      endif
    endif
    !
    if (associated(nodeLater)) then
      obj => nodeLater%GetItem()
      tsrLater => CastAsTimeSeriesRecordType(obj)
      if (associated(tsrLater)) then
        time1 = tsrLater%tsrTime
      endif
    endif
    !
    if (time0 > badtime) then
      ! Time0 is valid
      if (time1 > badtime) then
        ! Both time0 and time1 are valid
        if (time > time0 .and. time < time1) then
          ! Insert record between two list nodes
          obj => tsr
          call this%list%InsertBefore(obj, nodeLater)
        else
          ! No need to insert a time series record, but if existing record
          ! for time of interest has NODATA as tsrValue, replace tsrValue
          if (time == time0 .and. tsrEarlier%tsrValue == DNODATA .and. &
                  tsr%tsrValue /= DNODATA) then
            tsrEarlier%tsrValue = tsr%tsrValue
          elseif (time == time1 .and. tsrLater%tsrValue == DNODATA .and. &
                  tsr%tsrValue /= DNODATA) then
            tsrLater%tsrValue = tsr%tsrValue
          endif
        endif
      else
        ! Time0 is valid and time1 is invalid. Just add tsr to the list.
        call this%AddTimeSeriesRecord(tsr)
      endif
    else
      ! Time0 is invalid, so time1 must be for first node in list
      if (time1 > badtime) then
        ! Time 1 is valid
        if (time < time1) then
          ! Insert tsr at beginning of list
          obj => tsr
          call this%list%InsertBefore(obj, nodeLater)
        elseif (time == time1) then
          ! No need to insert a time series record, but if existing record
          ! for time of interest has NODATA as tsrValue, replace tsrValue
          if (tsrLater%tsrValue == DNODATA .and. tsr%tsrValue /= DNODATA) then
            tsrLater%tsrValue = tsr%tsrValue
          endif
        endif
      else
        ! Both time0 and time1 are invalid. Just add tsr to the list.
        call this%AddTimeSeriesRecord(tsr)
      endif
    endif
    !
    return
  end subroutine InsertTsr

  function FindLatestTime(this) result (endtime)
! ******************************************************************************
! FindLatestTime -- find latest time
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType), intent(inout) :: this
    ! -- local
    integer :: nrecords
    double precision :: endtime
    type(TimeSeriesRecordType), pointer :: tsr
    class(*), pointer :: obj
! ------------------------------------------------------------------------------
    !
    nrecords = this%list%Count()
    obj => this%list%GetItem(nrecords)
    tsr => CastAsTimeSeriesRecordType(obj)
    endtime = tsr%tsrTime
    !
    return
  end function FindLatestTime

  subroutine Clear(this, destroy)
! ******************************************************************************
! Clear -- Clear the list of time series records
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesType), intent(inout) :: this
    logical, optional,     intent(in)    :: destroy
! ------------------------------------------------------------------------------
    !
    call this%list%Clear(destroy)
    !
    return
  end subroutine Clear

! Type-bound procedures of TimeSeriesFileType

  function Count(this)
! ******************************************************************************
! Count --count number of time series
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- return
    integer(I4B) :: Count
    ! -- dummy
    class(TimeSeriesFileType) :: this
! ------------------------------------------------------------------------------
    !
    if (associated(this%timeSeries)) then
      Count = size(this%timeSeries)
    else
      Count = 0
    endif
    return
  end function Count

  function GetTimeSeries(this, indx) result (res)
! ******************************************************************************
! GetTimeSeries -- get ts
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesFileType) :: this
    integer(I4B), intent(in) :: indx
    ! result
    type(TimeSeriesType), pointer :: res
! ------------------------------------------------------------------------------
    !
    res => null()
    if (indx > 0 .and. indx <= this%nTimeSeries) then
      res => this%timeSeries(indx)
    endif
    return
  end function GetTimeSeries

  subroutine Initializetsfile(this, filename, iout, autoDeallocate)
! ******************************************************************************
! Initializetsfile -- Open time-series tsfile file and read options and first 
!   record, which may contain data to define multiple time series.
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesFileType), target, intent(inout) :: this
    character(len=*),           intent(in)    :: filename
    integer(I4B),                    intent(in)    :: iout
    logical, optional,          intent(in)    :: autoDeallocate
    ! -- local
    integer(I4B) :: iMethod, istatus, j, nwords
    integer(I4B) :: ierr, inunit
    logical :: autoDeallocateLocal = .true.
    logical :: continueread, found, endOfBlock
    real(DP) :: sfaclocal
    character(len=40) :: keyword, keyvalue
    character(len=LINELENGTH) :: ermsg
    character(len=LENHUGELINE)     :: line
    character(len=LENTIMESERIESNAME), allocatable, dimension(:) :: words
! ------------------------------------------------------------------------------
    !
    ! -- Initialize some variables
    if (present(autoDeallocate)) autoDeallocateLocal = autoDeallocate
    iMethod = UNDEFINED
    !
    ! -- Assign members
    this%iout = iout
    this%datafile = filename
    !
    ! -- Open the time-series tsfile input file
    this%inunit = GetUnit()
    inunit = this%inunit
    call openfile(inunit,0,filename,'TS6')
    !
    ! -- Initialize block parser
    call this%parser%Initialize(this%inunit, this%iout)
    !
    ! -- Read the ATTRIBUTES block and count time series
    continueread = .false.
    ierr = 0
    !
    ! -- get BEGIN line of ATTRIBUTES block
    call this%parser%GetBlock('ATTRIBUTES', found, ierr)
    if (ierr /= 0) then
      ! end of file
      ermsg = 'End-of-file encountered while searching for' // &
              ' ATTRIBUTES in time-series ' // &
              'input file "' // trim(this%datafile) // '"'
      call store_error(ermsg)
      call this%parser%StoreErrorUnit()
      call ustop()
    elseif (.not. found) then
      ermsg = 'ATTRIBUTES block not found in time-series ' // &
              'tsfile input file "' // trim(this%datafile) // '"'
      call store_error(ermsg)
      call this%parser%StoreErrorUnit()
      call ustop()
    endif
    !
    ! -- parse ATTRIBUTES entries
    do
      ! -- read a line from input
      call this%parser%GetNextLine(endOfBlock)
      if (endOfBlock) exit
      !
      ! -- get the keyword
      call this%parser%GetStringCaps(keyword)
      !
      ! support either NAME or NAMES as equivalent keywords
      if (keyword=='NAMES') keyword = 'NAME'
      !
      if (keyword /= 'NAME' .and. keyword /= 'METHODS' .and. keyword /= 'SFACS') then
        ! -- get the word following the keyword (the key value)
        call this%parser%GetStringCaps(keyvalue)
      endif
      !
      select case (keyword)
      case ('NAME')
!        line = line(istart:linelen)
        call this%parser%GetRemainingLine(line)
        call ParseLine(line, nwords, words, this%parser%iuactive)
        this%nTimeSeries = nwords
        ! -- Allocate the timeSeries array and initialize each
        !    time series.
        allocate(this%timeSeries(this%nTimeSeries))
        do j=1,this%nTimeSeries
          call this%timeSeries(j)%initialize_time_series(this, words(j), &
                  autoDeallocateLocal)
        enddo
      case ('METHOD')
        if (this%nTimeSeries == 0) then
          ermsg = 'Error: NAME attribute not provided before METHOD in file: ' &
                  // trim(filename)
          call store_error(ermsg)
          call this%parser%StoreErrorUnit()
          call ustop()
        endif
        select case (keyvalue)
        case ('STEPWISE')
          iMethod = STEPWISE
        case ('LINEAR')
          iMethod = LINEAR
        case ('LINEAREND')
          iMethod = LINEAREND
        case default
          ermsg = 'Unknown interpolation method: "' // trim(keyvalue) // '"'
          call store_error(ermsg)
        end select
        do j=1,this%nTimeSeries
          this%timeSeries(j)%iMethod = iMethod
        enddo
      case ('METHODS')
        if (this%nTimeSeries == 0) then
          ermsg = 'Error: NAME attribute not provided before METHODS in file: ' &
                  // trim(filename)
          call store_error(ermsg)
          call this%parser%StoreErrorUnit()
          call ustop()
        endif
        call this%parser%GetRemainingLine(line)
        call ParseLine(line, nwords, words, this%parser%iuactive)
        if (nwords < this%nTimeSeries) then
          ermsg = 'Error: METHODS attribute does not list a method for' // &
                  ' all time series.'
          call store_error(ermsg)
          call this%parser%StoreErrorUnit()
          call ustop()
        endif
        do j=1,this%nTimeSeries
          call upcase(words(j))
          select case (words(j))
          case ('STEPWISE')
            iMethod = STEPWISE
          case ('LINEAR')
            iMethod = LINEAR
          case ('LINEAREND')
            iMethod = LINEAREND
          case default
            ermsg = 'Unknown interpolation method: "' // trim(words(j)) // '"'
            call store_error(ermsg)
          end select
          this%timeSeries(j)%iMethod = iMethod
        enddo
      case ('SFAC')
        if (this%nTimeSeries == 0) then
          ermsg = 'Error: NAME attribute not provided before SFAC in file: ' &
                  // trim(filename)
          call store_error(ermsg)
          call this%parser%StoreErrorUnit()
          call ustop()
        endif
        read(keyvalue,*,iostat=istatus)sfaclocal
        if (istatus /= 0) then
          ermsg = 'Error reading numeric value from: "' // trim(keyvalue) // '"'
          call store_error(ermsg)
        endif
        do j=1,this%nTimeSeries
          this%timeSeries(j)%sfac = sfaclocal
        enddo
      case ('SFACS')
        if (this%nTimeSeries == 0) then
          ermsg = 'Error: NAME attribute not provided before SFACS in file: ' &
                  // trim(filename)
          call store_error(ermsg)
          call this%parser%StoreErrorUnit()
          call ustop()
        endif
        do j=1,this%nTimeSeries
          sfaclocal = this%parser%GetDouble()
          this%timeSeries(j)%sfac = sfaclocal
        enddo
      case ('AUTODEALLOCATE')
        do j=1,this%nTimeSeries
          this%timeSeries(j)%autoDeallocate = (keyvalue == 'TRUE')
        enddo
      case default
        ermsg = 'Unknown option found in ATTRIBUTES block: "' // &
                trim(keyword) // '"'
        call store_error(ermsg)
        call this%parser%StoreErrorUnit()
        call ustop()
      end select
    enddo
    !
    ! -- Get TIMESERIES block
    call this%parser%GetBlock('TIMESERIES', found, ierr, &
                              supportOpenClose=.true.)
    !
    ! -- Read the first line of time-series data
    if (.not. this%read_tsfile_line()) then
      ermsg = 'Error: No time-series data contained in file: ' // &
              trim(this%datafile)
      call store_error(ermsg)
    endif
    !
    ! -- Clean up and return
    if (allocated(words)) deallocate(words)
    !
    if (count_errors() > 0) then
      call this%parser%StoreErrorUnit()
      call ustop()
    endif
    !
    return
  end subroutine Initializetsfile

  logical function read_tsfile_line(this)
! ******************************************************************************
! read_tsfile_line -- read tsfile line
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesFileType), intent(inout) :: this
    ! -- local
    real(DP) :: tsrTime, tsrValue
    integer(I4B) :: i
    logical :: eof, endOfBlock
    type(TimeSeriesRecordType), pointer :: tsRecord => null()
! ------------------------------------------------------------------------------
    !
    eof = .false.
    read_tsfile_line = .false.
    !
    ! -- Get an arbitrary length, non-comment, non-blank line
    !    from the input file.
    call this%parser%GetNextLine(endOfBlock)
    !
    ! -- Get the time
    tsrTime = this%parser%GetDouble()
    !
    ! -- Construct a new record and append a new node to each time series
    tsloop: do i=1,this%nTimeSeries
      tsrValue = this%parser%GetDouble()
      if (tsrValue == DNODATA) cycle tsloop
      ! -- multiply value by sfac
      tsrValue = tsrValue * this%timeSeries(i)%sfac
      call ConstructTimeSeriesRecord(tsRecord, tsrTime, tsrValue)
      call AddTimeSeriesRecordToList(this%timeSeries(i)%list, tsRecord)
    enddo tsloop
    read_tsfile_line = .true.
    !
    return
  end function read_tsfile_line

  subroutine tsf_da(this)
! ******************************************************************************
! tsf_da -- deallocate
! ******************************************************************************
!
!    SPECIFICATIONS:
! ------------------------------------------------------------------------------
    ! -- dummy
    class(TimeSeriesFileType), intent(inout) :: this
    ! -- local
    integer :: i, n
    type(TimeSeriesType), pointer :: ts => null()
! ------------------------------------------------------------------------------
    !
    n = this%Count()
    do i=1,n
      ts => this%GetTimeSeries(i)
      if (associated(ts)) then
        call ts%da()
!        deallocate(ts)
      endif
    enddo
    !
    deallocate(this%timeSeries)
    deallocate(this%parser)
    !
    return
  end subroutine tsf_da

end module TimeSeriesModule
