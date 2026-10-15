package com.example.spr_swcup.service.Impl.history;

import com.example.spr_swcup.dto.history.*;
import com.example.spr_swcup.mapper.history.HistoryMapper;
import com.example.spr_swcup.mapper.history.QAMapper;
import com.example.spr_swcup.service.history.AudioFileService;
import com.example.spr_swcup.service.history.HistoryNotFoundException;
import com.example.spr_swcup.service.history.LandmarkImageService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class HistoryServiceImplTest {

  @Mock
  private HistoryMapper historyMapper;

  @Mock
  private QAMapper qaMapper;

  @Mock
  private AudioFileService audioFileService;

  @Mock
  private LandmarkImageService landmarkImageService;

  @InjectMocks
  private HistoryServiceImpl historyService;

  private static final String TEST_USER_ID = "testUser";
  private static final Integer TEST_HISTORY_ID = 1;

  @BeforeEach
  public void setUp() {

  }

  @Test
  public void getUserHistory_Success() {
    // 准备测试数据
    List<BasicHistoryDTO> mockHistoryList = Arrays.asList(
            new BasicHistoryDTO(), new BasicHistoryDTO());

    // 设置模拟行为
    when(historyMapper.getUserInterviewHistory(TEST_USER_ID))
            .thenReturn(mockHistoryList);

    // 执行测试
    UserHistoryResponse response = historyService.getUserHistory(TEST_USER_ID);

    // 验证结果
    assertNotNull(response);
    assertEquals(TEST_USER_ID, response.getUserId());
    assertEquals(2, response.getTotal());
    assertEquals(mockHistoryList, response.getHistoryList());

    // 验证模拟交互
    verify(historyMapper).getUserInterviewHistory(TEST_USER_ID);
  }

  @Test
  public void getUserHistory_WhenErrorOccurs_ThrowsException() {
    when(historyMapper.getUserInterviewHistory(TEST_USER_ID))
            .thenThrow(new RuntimeException("数据库错误"));

    // 使用assertThrows来捕获异常
    assertThrows(RuntimeException.class, () -> historyService.getUserHistory(TEST_USER_ID));
  }

  @Test
  public void getHistoryDetail_Success() {
    // 准备测试数据
    DetailedHistoryDTO mockHistory = new DetailedHistoryDTO();
    List<QADTO> mockQAList = Arrays.asList(new QADTO(), new QADTO());
    List<String> mockLandmarkImages = Arrays.asList("image1.jpg", "image2.jpg");

    // 设置模拟行为
    when(historyMapper.getInterviewHistoryById(TEST_HISTORY_ID))
            .thenReturn(mockHistory);
    when(qaMapper.getQAByHistoryId(TEST_HISTORY_ID))
            .thenReturn(mockQAList);
    when(audioFileService.filterQALogSkipFirstAnswer(mockQAList))
            .thenReturn(mockQAList);
    when(audioFileService.matchAudioFilesToQALog(eq(TEST_HISTORY_ID), any()))
            .thenReturn(mockQAList);
    when(landmarkImageService.getLandmarkImages(TEST_HISTORY_ID))
            .thenReturn(mockLandmarkImages);

    // 执行测试
    DetailedHistoryResponse response = historyService.getHistoryDetail(TEST_HISTORY_ID);

    // 验证结果
    assertNotNull(response);
    assertEquals(mockHistory, response.getInterviewHistory());
    assertEquals(mockQAList, response.getQaLog());
    assertEquals(mockLandmarkImages, response.getLandmarkImages());

    // 验证模拟交互
    verify(historyMapper).getInterviewHistoryById(TEST_HISTORY_ID);
    verify(qaMapper).getQAByHistoryId(TEST_HISTORY_ID);
    verify(audioFileService).filterQALogSkipFirstAnswer(any());
    verify(audioFileService).matchAudioFilesToQALog(eq(TEST_HISTORY_ID), any());
    verify(landmarkImageService).getLandmarkImages(TEST_HISTORY_ID);
  }

  @Test
  public void getHistoryDetail_WhenHistoryNotFound_ThrowsException() {
    when(historyMapper.getInterviewHistoryById(TEST_HISTORY_ID))
            .thenReturn(null);

    // 使用assertThrows来捕获异常
    assertThrows(HistoryNotFoundException.class, () -> historyService.getHistoryDetail(TEST_HISTORY_ID));
  }

  @Test
  public void getHistoryDetail_WhenAudioServiceFails_ContinuesWithoutError() {
    // 准备测试数据
    DetailedHistoryDTO mockHistory = new DetailedHistoryDTO();
    List<QADTO> mockQAList = Collections.singletonList(new QADTO());
    List<String> mockLandmarkImages = Collections.singletonList("image1.jpg");

    // 设置模拟行为
    when(historyMapper.getInterviewHistoryById(TEST_HISTORY_ID))
            .thenReturn(mockHistory);
    when(qaMapper.getQAByHistoryId(TEST_HISTORY_ID))
            .thenReturn(mockQAList);
    when(audioFileService.filterQALogSkipFirstAnswer(any()))
            .thenThrow(new RuntimeException("音频服务错误"));
    when(landmarkImageService.getLandmarkImages(TEST_HISTORY_ID))
            .thenReturn(mockLandmarkImages);

    // 执行测试
    DetailedHistoryResponse response = historyService.getHistoryDetail(TEST_HISTORY_ID);

    // 验证响应仍然包含基本数据
    assertNotNull(response);
    assertEquals(mockHistory, response.getInterviewHistory());
    assertEquals(mockQAList, response.getQaLog());
    assertEquals(mockLandmarkImages, response.getLandmarkImages());

    // 验证音频服务的方法被调用，即使抛出异常，后续地标图片服务仍然被调用
    verify(audioFileService).filterQALogSkipFirstAnswer(any());
    verify(landmarkImageService).getLandmarkImages(TEST_HISTORY_ID);
    // 注意：由于filterQALogSkipFirstAnswer抛出异常，因此matchAudioFilesToQALog方法不应该被调用
    verify(audioFileService, never()).matchAudioFilesToQALog(eq(TEST_HISTORY_ID), any());
  }
}